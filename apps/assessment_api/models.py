# Create your models here.
from django.contrib.auth.models import User
from django.db import models

from apps.assessment_api.managers import UserManager


class CustomUser(User):
    objects = UserManager()

    class Meta:
        proxy = True
