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
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
