from django import forms
from .models import Student
from .models import Application
from .models import Employer
from .models import JobSlot
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
    validate_password,
)


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "id_password"}
            # ),
            # help_text=password_validators_help_text_html(),
        )
    )

    class Meta:
        model = Student
        fields = [
            "full_name",
            "reg_no",
            "course",
            "department",
            "institution",
            "email",
            "phone_number",
            "national_id",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "reg_no": forms.TextInput(attrs={"class": "form-control"}),
            "course": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Computer Science"}
            ),
            "institution": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Maseno University"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "national_id": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. +2547********"}
            ),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "full_name",
            "course",
            "department",
            "year_of_study",
            "institution",
            "email",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "course": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Computer Science"}
            ),
            "year_of_study": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Year 3"}
            ),
            "institution": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Maseno University"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            # "national_id",
            "insurance_cover_no",
            "cv",
            "recommendation_letter",
            "cover_letter",
            "portfolio_link",
        ]

        widgets = {
            "cv": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf"}),
            "recommendation_letter": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf"}
            ),
            "cover_letter": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf"}
            ),
            # "national_id": forms.TextInput(
            # attrs={
            # "class": "form-control",
            # "type": "number",  # Forces numeric keypad on mobile
            # "placeholder": "e.g. 12345678",
            # }
            # ),
            "insurance_cover_no": forms.TextInput(attrs={"class": "form-control"}),
            "portfolio_link": forms.URLInput(attrs={"class": "form-control"}),
        }


class EmployerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text=password_validators_help_text_html(),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    company_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    industry = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = Employer
        fields = ["company_name", "industry", "location"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password:
            validate_password(password)

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobSlot
        # fields = ["title", "description", "requirements", "location", "deadline"]
        fields = [
            "title",
            "description",
            "requirements",
            "location",
            "field_of_study",
            "intake",
            "deadline",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Software Engineer"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City or Remote"}
            ),
            "field_of_study": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Computer Science",
                }
            ),
            "intake": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. May 2026 / Semester 2",
                }
            ),
            "deadline": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
        # widgets = {
        #   "title": forms.TextInput(
        #      attrs={"class": "form-control", "placeholder": "e.g. Software Engineer"}
        # ),
        # "location": forms.TextInput(
        #   attrs={"class": "form-control", "placeholder": "City or Remote"}
        #  "field_of_study": forms.TextInput(
        # attrs={
        #    "class": "form-control",
        #   "placeholder": "e.g. Computer Science",
        # }
        # ),
        # "intake": forms.TextInput(
        #   attrs={
        #      "class": "form-control",
        #     "placeholder": "e.g. May 2026 / Semester 2",
        # }
        # ),
        # ),
        # "deadline": forms.DateInput(
        #   attrs={"type": "date", "class": "form-control"}
        # ),
        # "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        # Add classes to other fields for Bootstrap styling
        # }


class ForgotCredentialsForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your registered email",
            }
        )
    )
