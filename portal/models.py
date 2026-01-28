from django.db import models
from django.contrib.auth.models import User  # Import the built-in User tool
from django.core.validators import (
    FileExtensionValidator,
    RegexValidator,
)  # Import this!

# Define the rules
id_validator = RegexValidator(r"^\d{7,8}$", "ID number must be 7 or 8 digits.")
insurance_validator = RegexValidator(
    r"^[A-Z0-9]{5,15}$", "Enter a valid Insurance/NHIF number."
)


# Create your models here.
class Student(models.Model):
    # This links the student to a login account
    # We use null=True so existing students don't break immediately
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    full_name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=25, unique=True)
    course = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.full_name


class Employer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class JobSlot(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # e.g. "Software Engineering Intern"
    description = models.TextField()
    deadline = models.DateField()
    requirements = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, default="Remote")

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name}"


class Application(models.Model):
    job = models.ForeignKey("JobSlot", on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    # New Required Details
    national_id = models.CharField(max_length=20)
    insurance_cover_no = models.CharField(max_length=50)

    # File Uploads (will be saved in a 'documents/' folder)
    cv = models.FileField(upload_to="applications/cvs/")
    recommendation_letter = models.FileField(upload_to="applications/recommendations/")
    cover_letter = models.FileField(upload_to="applications/cover_letters/")

    # Optional field
    portfolio_link = models.URLField(blank=True, null=True)
    # We now link applications to the User, not just a text name
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")
    cv = models.FileField(
        upload_to="applications/cvs/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    recommendation_letter = models.FileField(
        upload_to="applications/recommendations/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    cover_letter = models.FileField(
        upload_to="applications/cover_letters/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    national_id = models.CharField(
        max_length=8,
        validators=[id_validator],
        help_text="Enter your 7 or 8-digit National ID",
    )

    insurance_cover_no = models.CharField(
        max_length=15,
        validators=[insurance_validator],
        help_text="Enter your Insurance/NHIF policy number",
    )
    admin_feedback = models.TextField(
        blank=True, null=True, help_text="Reason for approval/rejection"
    )

    def __str__(self):
        return (
            "{self.student.username if self.student else 'Unknown'} - {self.job.title}"
        )


# class Firm(models.Model):
# user = models.OneToOneField(
#    User, on_delete=models.CASCADE, related_name="company_profile"
# )
# company_name = models.CharField(max_length=200)
# industry = models.CharField(max_length=100)
# location = models.CharField(max_length=100)
# website = models.URLField(blank=True)
# is_verified = models.BooleanField(default=False)  # Admin must toggle this to True

# def __str__(self):
#   return self.company_name
