from django.db import models
from django.contrib.auth.models import UserManager as DjangoUserManager

class UserQuerySet(models.QuerySet):
    def filter_by_site(self, site):
        return self.filter(userprofile__site=site)
    
    def filter_by_role(self, role):
        return self.filter(userprofile__role=role)

    def filter_by_language(self, language):
        return self.filter(userprofile__language=language)
    
    def filter_by_loginid(self, loginid):
        return self.filter(username=loginid).first()

class UserManager(DjangoUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def filter_users(self,site=None, role=None, language=None,loginid=None):
        Qset = self.get_queryset()
        Qset=Qset.filter(is_active=True,is_superuser=False).order_by('-userprofile__created_datetime')
        if site:
            Qset = Qset.filter_by_site(site)
        if role:
            Qset = Qset.filter_by_role(role)
        if language:
            Qset = Qset.filter_by_language(language)
        if loginid:
            Qset = Qset.filter_by_loginid(loginid)
        return Qset
    
    def read_recent50_profile(self):
        Qset=self.get_queryset()
        Qset=Qset.filter(is_active=True,is_superuser=False)
        return Qset.filter(is_active=True).select_related('userprofile').order_by('-userprofile__created_datetime')[:50]
    
