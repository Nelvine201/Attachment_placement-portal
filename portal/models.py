from django.db import models
from django.contrib.auth.models import User  # Import the built-in User tool
from django.core.validators import (
    FileExtensionValidator,
    RegexValidator,
)  # Import this!
from django.utils import timezone

# Define the rules
id_validator = RegexValidator(r"^\d{7,8}$", "ID number must be 7 or 8 digits.")
insurance_validator = RegexValidator(
    r"^[A-Z0-9]{5,15}$", "Enter a valid Insurance/NHIF number."
)


# Create your models here.
id_validator = RegexValidator(
    regex=r"^\d{8}$", message="National ID must be exactly 8 digits"
)


class Student(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    full_name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=25, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.CharField(max_length=30, blank=True)
    institution = models.CharField(max_length=150, blank=True)
    email = models.EmailField()

    national_id = models.CharField(max_length=8, validators=[id_validator], unique=True)

    # ⭐ Safe username getter (VERY IMPORTANT)
    def get_username(self):
        return self.user.username if self.user else ""

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
    # website = models.URLField(blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class JobSlot(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # e.g. "Software Engineering Intern"
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, default="Remote")
    field_of_study = models.CharField(max_length=120, blank=True)
    intake = models.CharField(max_length=50, blank=True)

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name}"


class Application(models.Model):
    job = models.ForeignKey(JobSlot, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    # national_id = models.CharField(max_length=8)
    insurance_cover_no = models.CharField(
        max_length=15, validators=[insurance_validator]
    )

    cv = models.FileField(
        upload_to="applications/cvs/", validators=[FileExtensionValidator(["pdf"])]
    )
    recommendation_letter = models.FileField(
        upload_to="applications/recommendations/",
        validators=[FileExtensionValidator(["pdf"])],
    )
    cover_letter = models.FileField(
        upload_to="applications/cover_letters/",
        validators=[FileExtensionValidator(["pdf"])],
    )

    portfolio_link = models.URLField(blank=True, null=True)

    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")
    placement_start_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    admin_feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "job")

    @property
    def placement_duration_days(self):
        if not self.placement_start_date:
            return None

        end_date = self.termination_date or timezone.now().date()
        duration = (end_date - self.placement_start_date).days
        return duration if duration >= 0 else None


class Job(models.Model):
    title = models.CharField(max_length=200)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateField()

    def is_open(self):
        from django.utils import timezone

        return self.deadline >= timezone.now().date()


class Notification(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.student.username}"


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
