from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Professor

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Student.objects.create(user=instance)
        elif instance.role == 'professor':
            Professor.objects.create(user=instance)