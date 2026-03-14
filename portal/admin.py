from django.contrib import admin

# Register your models here.

from .models import Student, Employer, JobSlot


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
