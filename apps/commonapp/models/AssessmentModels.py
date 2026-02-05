from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from .AuditField import AuditFieldModel


class Assessment(AuditFieldModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    num_of_questions = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.title


class Question(AuditFieldModel):
    QUESTION_TYPE = (
        ("MCQ", "Multiple Choice"),
        ("DESC", "Descriptive"),
    )

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE)

    def __str__(self):
        return self.text[:50]


class Option(AuditFieldModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

    def clean(self):
        if self.question.options.count() >= 5 and not self.pk:
            raise ValidationError("Each question can have a maximum 5 options")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
