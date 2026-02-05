from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from apps.assessment_api.managers import UserManager

class CustomUser(User):
    objects=UserManager()

    class Meta:
        proxy=True