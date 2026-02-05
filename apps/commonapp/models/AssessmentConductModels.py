from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import models

from .AuditField import AuditFieldModel


class AssessmentConduct(AuditFieldModel):
    CLOSURE_TYPE_CHOICES = [
        ("timeout", "Timeout"),
        ("user_end", "User Ended"),
        ("auto_close", "Auto Closed"),
    ]

    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conducts",
    )
    candidate = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessment_conducts",
    )

    # initially set when scheduling
    assessment_date = models.DateField()

    # filled after the candidate writes the assessment
    assessment_start_datetime = models.DateTimeField(null=True, blank=True)
    assessment_end_datetime = models.DateTimeField(null=True, blank=True)
    type_of_closure = models.CharField(
        max_length=20, choices=CLOSURE_TYPE_CHOICES, null=True, blank=True
    )

    duration = models.BigIntegerField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Assessment Conduct"
        verbose_name_plural = "Assessment Conducts"
        ordering = ["-assessment_date"]

    def __str__(self):
        user_str = self.user.username if self.user else "Deleted User"
        assessment_str = (
            self.assessment.title if self.assessment else "Deleted Assessment"
        )
        return f"{user_str} - {assessment_str} ({self.assessment_date})"

    def save(self, *args, **kwargs):
        # Auto-calculate duration once end time is available
        if self.assessment_start_datetime and self.assessment_end_datetime:
            assessment_starttime = self.assessment_start_datetime.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            assessment_endtime = self.assessment_end_datetime.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            assessment_starttime = datetime.strptime(
                assessment_starttime, "%Y-%m-%d %H:%M:%S"
            )
            assessment_endtime = datetime.strptime(
                assessment_endtime, "%Y-%m-%d %H:%M:%S"
            )
            # print(assessment_starttime,assessment_endtime)
            duration_in_seconds = (
                assessment_endtime - assessment_starttime
            ).total_seconds()
            self.duration = duration_in_seconds
        super().save(*args, **kwargs)
