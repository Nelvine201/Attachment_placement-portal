from django.contrib import admin
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import path
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
    change_list_template = "portal/application/change_list.html"
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download-full-report/",
                self.admin_site.admin_view(self.download_full_placement_report_csv),
                name="portal_application_download_full_report",
            ),
        ]
        return custom_urls + urls

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
        # response = HttpResponse(content_type="text/csv")
        # response["Content-Disposition"] = (
        # 'attachment; filename="admin_placement_tracking_report.csv"'
        return self._build_csv_response(
            queryset.select_related("student", "job", "job__employer"),
            filename="selected_applications_full_report.csv",
        )

    def download_full_placement_report_csv(self, request):
        queryset = Application.objects.select_related("student", "job", "job__employer")
        return self._build_csv_response(
            queryset,
            filename="all_applications_full_report.csv",
        )

    def _build_csv_response(self, queryset, *, filename):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                # "Name",
                "Application ID",
                "Student Name",
                "Registration Number",
                "Student Email",
                "National ID",
                "Course",
                "Year of Study",
                "Institution",
                # "Company",
                "Job Title",
                "Employer Company",
                "Employer Industry",
                "Employer Contact Email",
                "Job Location",
                "Insurance Cover Number",
                "Portfolio Link",
                "CV File",
                "Recommendation Letter File",
                "Cover Letter File",
                "Date Applied",
                "Placement Start Date",
                "Termination Date",
                # "Application Status",
                "Duration (days)",
                "Application Status",
                "Admin Feedback",
            ]
        )

        # for app in queryset.select_related("student", "job", "job__employer"):
        for app in queryset:
            writer.writerow(
                [
                    app.id,
                    app.student.full_name or app.student.user.username,
                    app.student.reg_no,
                    app.student.email,
                    app.student.national_id,
                    app.student.course or "N/A",
                    app.student.year_of_study or "N/A",
                    app.student.institution or "N/A",
                    app.job.title,
                    app.job.employer.company_name,
                    # app.applied_on.date(),
                    app.job.employer.industry or "N/A",
                    app.job.employer.contact_email or "N/A",
                    app.job.location or "N/A",
                    app.insurance_cover_no,
                    app.portfolio_link or "",
                    app.cv.url if app.cv else "",
                    app.recommendation_letter.url if app.recommendation_letter else "",
                    app.cover_letter.url if app.cover_letter else "",
                    app.applied_on,
                    app.placement_start_date or "",
                    (
                        app.placement_duration_days
                        if app.placement_duration_days is not None
                        else ""
                    ),
                    app.termination_date or "",
                    app.status,
                    app.admin_feedback or "",
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
