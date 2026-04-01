"""
URL configuration for placement_sys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from portal import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register_student, name="register"),
    path("jobs/", views.job_list, name="jobs"),
    path("apply/<int:job_id>/", views.apply_for_job, name="apply_for_job"),
    # path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
    ),
    # path("signup/", views.signup_view, name="signup"),
    # path("register/", views.register, name="register"),
    # recovery and reset of passwords
    path("forgot-credentials/", views.forgot_credentials, name="forgot_credentials"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="portal/password_reset_form.html",
            email_template_name="portal/password_reset_email.txt",
            subject_template_name="portal/password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="portal/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="portal/password_reset_confirm.html",
            success_url="/password-reset-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="portal/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("dashboard/redirect/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/employer/", views.employer_dashboard, name="employer_dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    # In urls.py
    path("register/employer/", views.register_employer, name="register_employer"),
    path("post-job/", views.post_job, name="post_job"),
    # path( "status/update/<int:app_id>/<str:new_status>/",views.update_application_status,name="update_status",),
    # path("status/update/<int:application_id>/<str:new_status>/", views.update_application_status)
    path(
        "status/update/<int:app_id>/<str:new_status>/",
        views.update_application_status,
        name="update_application_status",
    ),
    path(
        "student/review/<int:student_id>/", views.review_student, name="review_student"
    ),
    path("job/edit/<int:job_id>/", views.edit_job, name="edit_job"),
    path("job/delete/<int:job_id>/", views.delete_job, name="delete_job"),
    path("register/choice/", views.register_choice, name="register_choice"),
    path("register/student/", views.register_student, name="register_student"),
    path("register/employer/", views.register_employer, name="register_employer"),
    path("dashboard/active-slots/", views.active_slots, name="active_slots"),
    path("dashboard/applications/", views.all_applications, name="all_applications"),
    path("job/<int:job_id>/", views.job_detail, name="job_detail"),
    path("application/<int:pk>/", views.application_detail, name="application_detail"),
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notification/<int:pk>/", views.notification_detail, name="notification_detail"
    ),
    path("about/", views.about, name="about"),
    path(
        "dashboard/employer/application/<int:application_id>/review/",
        views.review_application_documents,
        name="review_application_documents",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
