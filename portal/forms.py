from django import forms
from .models import Student
from .models import Application
from .models import Employer
from .models import JobSlot


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Student
        fields = ["full_name", "reg_no", "course", "email"]
        # This adds Bootstrap styling to the input boxes
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Full Name"}
            ),
            "reg_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. CI/001/2022"}
            ),
            "course": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. BSc. Computer Science",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. student@maseno.ac.ke",
                }
            ),
        }


# portal/forms.py
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["full_name", "course", "email"]  # Fields the student can change
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "course": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "national_id",
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
            "national_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "number",  # Forces numeric keypad on mobile
                    "placeholder": "e.g. 12345678",
                }
            ),
            "insurance_cover_no": forms.TextInput(attrs={"class": "form-control"}),
            "portfolio_link": forms.URLInput(attrs={"class": "form-control"}),
        }


class EmployerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
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
        fields = ["company_name", "industry", "location", "website"]
        widgets = {
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobSlot
        fields = ["title", "description", "requirements", "location", "deadline"]
        widgets = {
            "deadline": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            # Add classes to other fields for Bootstrap styling
        }
