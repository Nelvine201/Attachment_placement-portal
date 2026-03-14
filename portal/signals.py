from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Student


# @receiver(post_save, sender=User)
# def create_student_profile(sender, instance, created, **kwargs):
#   if created:
#      # Only create student profile if user is NOT employer/admin
#     if not hasattr(instance, "employer_profile"):
#        Student.objects.get_or_create(
#           user=instance,
#          defaults={
#             "full_name": instance.username,
#             "reg_no": "TEMP_" + instance.username,
#            "course": "Not Set",
#           "email": instance.email or "",
#      },
# )
