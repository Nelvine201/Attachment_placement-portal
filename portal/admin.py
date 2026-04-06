from django.contrib import admin
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
import csv

# Register your models here.
from .models import Student, Employer, JobSlot, Application


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "is_verified")
    list_filter = ("is_verified",)
    search_fields = ("company_name",)
    list_editable = ("is_verified",)  # Quick approval from the list
    actions = ["verify_employers"]

    def verify_employers(self, request, queryset):
        queryset.update(is_verified=True)

    verify_employers.short_description = "verify selected employers"


@admin.register(JobSlot)
class JobSlotAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "location", "deadline", "created_at")
    list_filter = ("employer", "deadline")
    search_fields = ("title", "description")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "reg_no",
        "course",
        "year_of_study",
        "institution",
        "national_id",
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_title",
        "employer_company",
        "student_name",
        "course",
        "year_of_study",
        "institution",
        "termination_date",
        "duration_days",
        "status",
        "applied_on",
        "insurance_cover_no",
    )
    list_filter = ("status", "applied_on", "termination_date", "job__employer")
    search_fields = (
        "student__full_name",
        "student__reg_no",
        "student__email",
        "student__institution",
        "job__title",
        "job__employer__company_name",
        "insurance_cover_no",
    )
    readonly_fields = ("applied_on", "duration_days")
    list_select_related = ("job", "job__employer", "student")
    date_hierarchy = "applied_on"
    actions = ["download_selected_placement_report_csv"]

    @admin.display(description="Slot")
    def job_title(self, obj):
        return obj.job.title

    @admin.display(description="Employer")
    def employer_company(self, obj):
        return obj.job.employer.company_name

    @admin.display(description="Student Name")
    def student_name(self, obj):
        return obj.student.full_name or obj.student.user.username

    @admin.display(description="Course")
    def course(self, obj):
        return obj.student.course

    @admin.display(description="Year of Study")
    def year_of_study(self, obj):
        return obj.student.year_of_study or "N/A"

    @admin.display(description="Institution")
    def institution(self, obj):
        return obj.student.institution or "N/A"

    @admin.display(description="Duration (days)")
    def duration_days(self, obj):
        return (
            obj.placement_duration_days
            if obj.placement_duration_days is not None
            else "N/A"
        )

    @admin.action(description="Download selected placement report rows (CSV)")
    def download_selected_placement_report_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="admin_placement_tracking_report.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Name",
                "Course",
                "Year of Study",
                "Institution",
                "Company",
                "Date Applied",
                "Termination Date",
                "Application Status",
                "Duration (days)",
            ]
        )

        for app in queryset.select_related("student", "job", "job__employer"):
            writer.writerow(
                [
                    app.student.full_name or app.student.user.username,
                    app.student.course or "N/A",
                    app.student.year_of_study or "N/A",
                    app.student.institution or "N/A",
                    app.job.employer.company_name,
                    app.applied_on.date(),
                    app.termination_date or "",
                    app.status,
                    (
                        app.placement_duration_days
                        if app.placement_duration_days is not None
                        else ""
                    ),
                ]
            )
        return response

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = (
                Application.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )

        super().save_model(request, obj, form, change)

        if (
            change
            and obj.student
            and obj.student.email
            and obj.status in ["Approved", "Rejected"]
            and previous_status != obj.status
        ):
            send_mail(
                subject=f"Application {obj.status}: {obj.job.title}",
                message=(
                    f"Hello {obj.student.username},\n\n"
                    f"Your application for '{obj.job.title}' has been {obj.status.lower()}.\n"
                    f"Feedback: {obj.admin_feedback or 'No additional feedback provided.'}\n\n"
                    "Please log in to your dashboard for more details."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[obj.student.email],
                fail_silently=True,
            )
