# from django.shortcuts import render


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm
from .forms import JobApplicationForm, StudentProfileForm, EmployerRegistrationForm
from .models import JobSlot, Application, Student, Employer, Notification
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import login, authenticate
from .forms import ForgotCredentialsForm
from django.urls import reverse
from django.conf import settings

from .forms import JobPostForm


# Create your views here.
def home(request):
    # This tells Django to look for home.html inside our templates folder
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


# def about(request):
#   return render(request, "about.html")


def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            reg_no = form.cleaned_data.get("reg_no")
            email = form.cleaned_data.get("email")
            course = form.cleaned_data.get("course")
            password = form.cleaned_data.get("password")
            national_id = form.cleaned_data.get("national_id")

            # Check if reg_no already exists
            if User.objects.filter(username=reg_no).exists():
                messages.error(
                    request, "A student with this Registration Number already exists."
                )
                return render(request, "portal/register.html", {"form": form})

            # Check if national ID already exists
            if Student.objects.filter(national_id=national_id).exists():
                messages.error(request, "National ID already exists.")
                return render(request, "portal/register.html", {"form": form})

            # Create login account
            user = User.objects.create_user(
                username=reg_no, email=email, password=password
            )

            # Create student profile
            Student.objects.create(
                user=user,
                full_name=full_name,
                reg_no=reg_no,
                email=email,
                course=course,
                national_id=national_id,
            )

            messages.success(request, "Registration successful! Please login.")
            return redirect("login")

    else:
        form = StudentRegistrationForm()

    return render(request, "portal/register.html", {"form": form})


# password recovery........
def forgot_credentials(request):
    if request.method == "POST":
        form = ForgotCredentialsForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            users = User.objects.filter(email__iexact=email)

            if users.exists():
                usernames = "\n".join(f"- {u.username}" for u in users)
                reset_link = request.build_absolute_uri(reverse("password_reset"))
                send_mail(
                    subject="CareerBridge account recovery",
                    message=(
                        "We received your account recovery request.\n\n"
                        f"Usernames linked to this email:\n{usernames}\n\n"
                        f"To reset password, visit: {reset_link}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )

            messages.success(
                request,
                "If an account exists with that email, recovery details have been sent.",
            )
            return redirect("login")
    else:
        form = ForgotCredentialsForm()

    return render(request, "portal/forgot_credentials.html", {"form": form})


# students dashboard....
@login_required
def student_dashboard(request):
    try:
        student_profile = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect("dashboard_redirect")

    # Correct filtering
    applications = Application.objects.filter(student=student_profile)
    notifications = Notification.objects.filter(student=request.user).order_by(
        "-created_at"
    )

    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(
        request,
        "portal/student_dashboard.html",
        {
            "student": student_profile,
            "applications": applications,
            "notifications": notifications[:5],
            "unread_notifications_count": unread_notifications_count,
        },
    )


@login_required
def edit_profile(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("dashboard")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, "portal/edit_profile.html", {"form": form})


@login_required
def dashboard_redirect(request):

    if hasattr(request.user, "employer_profile"):
        return redirect("employer_dashboard")

    elif hasattr(request.user, "student_profile"):
        return redirect("student_dashboard")

    elif request.user.is_superuser:
        return redirect("/admin/")

    return redirect("home")


@login_required
def employer_dashboard(request):

    try:
        employer = Employer.objects.get(user=request.user)
    except Employer.DoesNotExist:
        return redirect("dashboard_redirect")

    my_jobs = JobSlot.objects.filter(employer=employer)

    applications = Application.objects.filter(job__employer=employer).select_related(
        "student", "job"
    )
    pending_apps = applications.filter(status="Pending")
    accepted_apps = applications.filter(status="Accepted")
    rejected_apps = applications.filter(status="Rejected")

    context = {
        "employer": employer,
        "my_jobs": my_jobs,
        "applications": applications,
        "pending_apps": pending_apps,
        "accepted_apps": accepted_apps,
        "rejected_apps": rejected_apps,
    }

    return render(request, "portal/employer_dashboard.html", context)


@login_required
def job_list(request):
    jobs = JobSlot.objects.all()

    # Default value
    applied_job_ids = []

    # If user is logged in, check applications
    if request.user.is_authenticated:
        try:
            student_profile = request.user.student_profile

            applied_job_ids = Application.objects.filter(
                student=student_profile
            ).values_list("job_id", flat=True)

        except Student.DoesNotExist:
            applied_job_ids = []

    return render(
        request,
        "portal/job_list.html",
        {
            "jobs": jobs,
            "applied_job_ids": applied_job_ids,
        },
    )


@login_required(login_url="signup")
def apply_for_job(request, job_id):
    job = get_object_or_404(JobSlot, id=job_id)
    student = get_object_or_404(Student, user=request.user)

    if job.deadline < timezone.now().date():
        messages.error(request, "Application deadline has passed.")
        return redirect("jobs")

    already_applied = Application.objects.filter(student=student, job=job).exists()

    if already_applied:
        messages.warning(
            request,
            f"You have already applied for the {job.title} position at {job.employer.company_name}.",
        )
        return redirect("student_dashboard")

    if request.method == "POST":
        # request.FILES is required for CV and Letters
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = student
            application.save()
            # --- SEND EMAIL ---
            subject = f"Application Received: {job.title}"
            message = f"Hi {request.user.first_name},\n\nYour application for {job.title} at {job.employer.company_name} has been received successfully. You can track your status on your dashboard."
            recipient_list = [request.user.email]

            try:
                send_mail(subject, message, "portal@maseno.ac.ke", recipient_list)
            except Exception as e:
                print(f"Email failed: {e}")
            # ------------------

            messages.success(
                request, "Application submitted! Check your email for confirmation."
            )
            return redirect("dashboard")
    else:
        form = JobApplicationForm()

    return render(request, "portal/apply_form.html", {"form": form, "job": job})


@login_required
def review_student(request, student_id):
    # 1. Get the student profile
    try:
        student_profile = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        student_profile = get_object_or_404(Student, user__id=student_id)

    # 2. Get the employer profile
    employer_profile = get_object_or_404(Employer, user=request.user)

    # 3. Use 'applications' (plural) and remove .first()
    # This ensures the template loop {% for app in applications %} works
    applications = Application.objects.filter(
        student=student_profile,
        job__employer=employer_profile,
    )
    return render(
        request,
        "portal/review_student.html",
        {
            "student": student_profile,
            "applications": applications,  # <--- Changed this name and value
        },
    )


@login_required
def edit_job(request, job_id):
    # Ensure only the employer who created the job can edit it
    job = get_object_or_404(JobSlot, id=job_id, employer__user=request.user)

    if request.method == "POST":
        # 'instance=job' is the magic part—it tells Django to update the existing record
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("employer_dashboard")
    else:
        form = JobPostForm(instance=job)

    return render(
        request, "portal/post_job.html", {"form": form, "edit_mode": True, "job": job}
    )


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobSlot, id=job_id, employer__user=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully!")
    return redirect("employer_dashboard")


# login view......


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard_redirect")

        messages.error(request, "Invalid username or password")

    return render(request, "portal/login.html")


# post job
@login_required
def post_job(request):

    employer = get_object_or_404(Employer, user=request.user)

    if not employer.is_verified:
        return render(request, "portal/not_approved.html")

    if request.method == "POST":
        form = JobPostForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer
            job.save()

            return redirect("employer_dashboard")

    else:
        form = JobPostForm()

    return render(request, "portal/post_job.html", {"form": form})


# update status----


# employer register
def register_employer(request):
    if request.method == "POST":
        form = EmployerRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data.get("email", "")
            password = form.cleaned_data["password"]

            # Prevent duplicate usernames
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("register_employer")

            # Create login account (password hashed automatically)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            # Create employer profile
            Employer.objects.create(
                user=user,
                company_name=form.cleaned_data["company_name"],
                location=form.cleaned_data["location"],
                industry=form.cleaned_data["industry"],
                contact_email=form.cleaned_data.get("email", ""),
            )

            messages.success(
                request, "Employer registered successfully. You can now login."
            )
            return redirect("login")

        else:
            print(form.errors)
            return render(request, "portal/register_employer.html", {"form": form})

    else:
        form = EmployerRegistrationForm()
        return render(request, "portal/register_employer.html", {"form": form})


# login(request, user)

# return redirect("dashboard_redirect")

# else:
#   print(form.errors)


# return render(request, "portal/register_employer.html", {"form": form})
def register_choice(request):
    return render(request, "portal/register_choice.html")


@login_required
def active_slots(request):
    employer = get_object_or_404(Employer, user=request.user)

    jobs = JobSlot.objects.filter(
        employer=employer, deadline__gte=timezone.now().date()
    )

    return render(request, "portal/active_slots.html", {"jobs": jobs})


@login_required
def all_applications(request):
    employer = get_object_or_404(Employer, user=request.user)

    applications = Application.objects.filter(job__employer=employer).select_related(
        "student", "job"
    )

    return render(
        request, "portal/all_applications.html", {"applications": applications}
    )


def job_detail(request, job_id):
    job = JobSlot.objects.get(id=job_id)

    applied = False
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            applied = Application.objects.filter(student=student, job=job).exists()
        except Student.DoesNotExist:
            pass

    context = {
        "job": job,
        "today": timezone.now().date(),
        "applied": applied,
    }

    return render(request, "portal/job_detail.html", context)


def application_detail(request, pk):
    application = get_object_or_404(Application, id=pk)
    return render(
        request, "student/application_detail.html", {"application": application}
    )


@login_required
def review_application_documents(request, application_id):
    employer = get_object_or_404(Employer, user=request.user)
    application = get_object_or_404(
        Application, id=application_id, job__employer=employer
    )

    documents = [
        {"label": "Curriculum Vitae (CV)", "file": application.cv},
        {"label": "Recommendation Letter", "file": application.recommendation_letter},
        {"label": "Cover Letter", "file": application.cover_letter},
    ]

    return render(
        request,
        "portal/review_application_documents.html",
        {"application": application, "documents": documents},
    )


@login_required
def update_application_status(request, app_id, new_status):

    application = Application.objects.get(id=app_id)
    application.status = new_status
    application.save()

    student_email = application.student.user.email

    message = f"""
Hello {application.student.user.username},

Your application for {application.job.title}
has been {new_status}.

Please login to SCI Portal to download your letter.
"""

    send_mail(
        "SCI Portal Application Update",
        message,
        "portal@sci.com",
        [student_email],
        fail_silently=False,
    )

    Notification.objects.create(
        student=application.student.user,
        message=f"Your application for {application.job.title} has been {new_status}. Check your email and download your letter.",
    )

    return redirect("employer_dashboard")


def notifications(request):

    notifications = Notification.objects.filter(student=request.user).order_by(
        "-created_at"
    )

    notifications.update(is_read=True)

    return render(request, "notifications.html", {"notifications": notifications})


def notification_detail(request, pk):

    notification = get_object_or_404(Notification, id=pk)

    notification.is_read = True
    notification.save()

    return render(request, "notification_detail.html", {"notification": notification})
