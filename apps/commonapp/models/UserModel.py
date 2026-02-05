from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import models

from .AuditField import AuditFieldModel

User = get_user_model()
    
class UserProfile(AuditFieldModel):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Candidate', 'Candidate'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    site=models.CharField(max_length=100,blank=True,null=True)
    language=models.CharField(max_length=50,blank=True,null=True)
    candpassword=models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_superuser_profile(sender, instance, created, **kwargs):
    # Only run when a new user is created and that user is a superuser
    if created and instance.is_superuser:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'Admin'}
        )