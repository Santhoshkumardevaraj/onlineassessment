from django.db import models

from .AuditField import AuditFieldModel


class TypeLookup(AuditFieldModel):
    datafield = models.CharField(max_length=255)
    datafor = models.CharField(max_length=255)
    dataparamtext = models.CharField(max_length=255)
    dataparamvalue = models.CharField(max_length=255)

    def __str__(self):
        return self.datafield
