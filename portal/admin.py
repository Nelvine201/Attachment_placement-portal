from django.contrib import admin

# Register your models here.

from .models import Student, Employer, JobSlot


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    # This adds columns to the list view so you don't have to click each one
    # list_display = ("company_name", "user", "is_approved")
    # list_filter = ("is_approved",)  # Adds a filter sidebar
    pass
    search_fields = ("company_name",)
    actions = ["approve_employers"]

    def approve_employers(self, request, queryset):
        queryset.update(is_approved=True)

    approve_employers.short_description = "Approve selected employers"


admin.site.register(JobSlot)
# class StudentAdmin(admin.ModelAdmin):
# This tells Django which columns to show in the table
# list_display = ("full_name", "reg_no", "course", "email")
# This adds a search bar
# search_fields = ("full_name", "reg_no")
# list_display = ('company_name', 'user', 'is_approved')
# list_filter = ('is_approved',) # Adds a filter sidebar
# search_fields = ('company_name',)
# actions = ['approve_employers']
# def approve_employers(self, request, queryset):
#       queryset.update(is_approved=True)
#  approve_employers.short_description = "Approve selected employers"

# admin.site.register(JobSlot)

# admin.site.register(Student, StudentAdmin)
# admin.site.register(Employer)
# admin.site.register(JobSlot)
