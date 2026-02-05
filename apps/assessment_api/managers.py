from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from apps.commonapp.Utility import UtilityMaster as UTM


class UserQuerySet(models.QuerySet):
    def filter_by_role(self, role):
        return self.filter(userprofile__role=role)

    def filter_by_language(self, language):
        return self.filter(userprofile__language=language)

    def filter_by_site(self, site):
        return self.filter(userprofile__site=site)

    def filter_by_loginid(self, loginid):
        return self.filter(username=loginid)

    def filter_by_loginidmatch(self, loginidmatch):
        return self.filter(username__icontains=loginidmatch)


class UserManager(DjangoUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def filter_users(
        self, site=None, role=None, language=None, loginid=None, loginidmatch=None
    ):
        Qset = self.get_queryset()

        if site:
            Qset = Qset.filter_by_site(site)
        if role:
            Qset = Qset.filter_by_role(role)
        if language:
            Qset = Qset.filter_by_language(language)
        if loginid:
            Qset = Qset.filter_by_loginid(loginid)
        if loginidmatch:
            Qset = Qset.filter_by_loginidmatch(loginidmatch)
        Qset = Qset.filter(is_active=True, is_superuser=False).order_by(
            "-userprofile__created_datetime"
        )

        if loginidmatch:
            Qset = Qset[:30]

        return Qset
