# from django.shortcuts import render


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm
from .forms import JobApplicationForm, StudentProfileForm, EmployerRegistrationForm
from .models import JobSlot, Application, Student, Employer
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate

from .forms import JobPostForm


# Create your views here.
def home(request):
    # This tells Django to look for home.html inside our templates folder
    return render(request, "home.html")


def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # 1. Get the data from the cleaned form
            full_name = form.cleaned_data.get("full_name")
            reg_no = form.cleaned_data.get("reg_no")
            email = form.cleaned_data.get("email")
            course = form.cleaned_data.get("course")
            password = form.cleaned_data.get("password")

            # 2. Check if user already exists
            if not User.objects.filter(username=reg_no).exists():
                # 3. Create the Login Account (Security Engine)
                user = User.objects.create_user(
                    username=reg_no, email=email, password=password
                )

                # 4. Create the Student Profile (Your original details)
                # We link it to the user we just created
                Student.objects.create(
                    user=user,
                    full_name=full_name,
                    reg_no=reg_no,
                    email=email,
                    course=course,
                )

                messages.success(
                    request,
                    "Registration successful! Please login with your Reg No and Password.",
                )
                return redirect("login")
            else:
                messages.error(
                    request, "A student with this Registration Number already exists."
                )
    else:
        # If it's a GET request, just show the empty form
        form = StudentRegistrationForm()

    return render(request, "portal/register.html", {"form": form})


@login_required
def student_dashboard(request):
    # Get the student profile and their applications
    # We use 'filter' to show only applications for the logged-in student
    my_applications = Application.objects.filter(student=request.user)

    # Try to find the student profile details
    try:
        student_profile = request.user.student
    except Student.DoesNotExist:
        student_profile = None

    return render(
        request,
        "portal/dashboard.html",
        {"applications": my_applications, "profile": student_profile},
    )


@login_required
def student_dashboard(request):
    # 1. Get the student profile linked to the logged-in user
    try:
        # Use the related_name we discussed or filter manually
        student_profile = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect("dashboard_redirect")

    # 2. Filter applications
    # If Application model has 'student = ForeignKey(User)', use request.user
    # If Application model has 'student = ForeignKey(Student)', use student_profile

    # Based on your error, try changing it to this:
    applications = Application.objects.filter(student=request.user)

    # IF THAT FAILS, try:
    # applications = Application.objects.filter(student=student_profile)

    return render(
        request,
        "portal/student_dashboard.html",
        {"student": student_profile, "applications": applications},
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
    # Check if the user is an Employer
    if hasattr(request.user, "employer_profile"):
        return redirect("employer_dashboard")

    # Check if the user is a Student
    elif hasattr(request.user, "student_profile"):
        return redirect("student_dashboard")

    # If it's just a superuser (admin)
    elif request.user.is_superuser:
        return redirect("/admin/")

    else:
        # If they somehow have no profile, send them to a generic page or logout
        return render(request, "portal/no_profile.html")


@login_required
def employer_dashboard(request):
    # Get the employer profile linked to the user
    employer = get_object_or_404(Employer, user=request.user)

    # Get all jobs posted by this Employer
    my_jobs = JobSlot.objects.filter(employer=employer)

    # Get all applications for those jobs
    applications = Application.objects.filter(job__employer=employer).order_by(
        "-applied_on"
    )

    context = {
        "employer": employer,
        "my_jobs": my_jobs,
        "applications": applications,
    }
    return render(request, "portal/employer_dashboard.html", context)


def job_list(request):
    jobs = JobSlot.objects.all()

    # If the user is logged in, we find the jobs they already applied for
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(
            student=request.user  # Changed from student_email="test@..."
        ).values_list("job_id", flat=True)
    else:
        applied_job_ids = []

    return render(
        request,
        "portal/job_list.html",
        {"jobs": jobs, "applied_job_ids": applied_job_ids},
    )


@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(JobSlot, id=job_id)

    if request.method == "POST":
        # request.FILES is required for CV and Letters
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = request.user
            application.save()
            # --- SEND EMAIL ---
            subject = f"Application Received: {job.title}"
            message = f"Hi {request.user.first_name},\n\nYour application for {job.title} at {job.company_name} has been received successfully. You can track your status on your dashboard."
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


def register_employer(request):
    if request.method == "POST":
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            # 1. First, create the User (the account)
            # We use commit=False so we can handle it before saving to the DB
            employer_instance = form.save(commit=False)

            # 2. IMPORTANT: We need to create/find the user account first.
            # Usually, in these types of forms, the User is created inside
            # the form's own save method, or you need to create it here.

            # Try this logic:
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                email=form.cleaned_data.get("email", ""),
            )

            # 3. NOW link the user to the employer instance
            employer_instance.user = user
            employer_instance.save()

            # 4. Log them in and go to the dashboard
            login(request, user)
            return redirect("employer_dashboard")
    else:
        form = EmployerRegistrationForm()
    return render(request, "portal/register_employer.html", {"form": form})


@login_required
def post_job(request):
    # 1. Get the employer profile
    employer = get_object_or_404(Employer, user=request.user)

    # 2. Check Approval Status
    if not employer.is_approved:
        return render(request, "portal/not_approved.html")

    # 3. Handle Form Submission
    if request.method == "POST":
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer  # Automatically link the job to this employer
            job.save()
            return redirect("employer_dashboard")
    else:
        form = JobPostForm()

    return render(request, "portal/post_job.html", {"form": form})
