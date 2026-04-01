from django.contrib import admin
from django.conf import settings
from django.core.mail import send_mail

# Register your models here.

from .models import Student, Employer, JobSlot, Application


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "is_verified")
    list_filter = ("is_verified",)
    search_fields = ("company_name",)
    pass
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
    list_display = ("user", "full_name", "reg_no", "course", "national_id")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_title",
        "employer_company",
        "student_name",
        "student_username",
        "student_email",
        "status",
        "applied_on",
        "insurance_cover_no",
    )
    list_filter = ("status", "applied_on", "job__employer")
    search_fields = (
        "student__user__username",
        "student__user__email",
        "student__student_profile__full_name",
        "job__title",
        "job__employer__company_name",
        "insurance_cover_no",
    )
    readonly_fields = ("applied_on",)
    list_select_related = ("job", "job__employer", "student")

    @admin.display(description="Slot")
    def job_title(self, obj):
        return obj.job.title

    @admin.display(description="Employer")
    def employer_company(self, obj):
        return obj.job.employer.company_name

    @admin.display(description="Student Name")
    def student_name(self, obj):
        if hasattr(obj.student, "student_profile"):
            return obj.student.student_profile.full_name
        return obj.student.user.username

    @admin.display(description="Student Username")
    def student_username(self, obj):
        return obj.student.user.username

    @admin.display(description="Student Email")
    def student_email(self, obj):
        return obj.student.user.email

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
