from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class AuditFieldModel(models.Model):
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created',db_column="created_by_id",)
    created_datetime = models.DateTimeField(auto_now_add=True)    
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_modified",
        db_column="modified_by_id",
    )
    modified_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        current_user = kwargs.pop("user", None)
        now = timezone.now()

        if not self.pk:
            if current_user:
                self.created_by=current_user
            self.created_datetime=now
        # if record edited
        if  self.pk:           
            if current_user:
                self.modified_by = current_user
            self.modified_datetime = now

        super().save(*args, **kwargs)
    
    def deactivate(self, user=None):
        self.active = False
        if user:
            self.modified_by = user
        self.save(update_fields=['active', 'modified_by', 'modified_datetime'])

       