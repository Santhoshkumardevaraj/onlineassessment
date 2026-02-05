from django.db import models
from .AuditField import AuditFieldModel
from django.contrib.auth import get_user_model
User = get_user_model()

class CandidateAnswer(AuditFieldModel):
    candidate = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='candidate_answers',null=True,
        blank=True)
    assessment = models.ForeignKey('Assessment', on_delete=models.SET_NULL, related_name='candidate_answers',null=True,
        blank=True)
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, related_name='candidate_answers',null=True,
        blank=True)
    assessmentconduct = models.ForeignKey('AssessmentConduct', on_delete=models.SET_NULL, related_name='candidate_answers',null=True,
        blank=True)

    selected_option = models.ForeignKey(
        'Option',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='candidate_answers'
    )

    question_status = models.CharField(
        max_length=10,
        null=True,   # null = not viewed
        blank=True
    )

    is_correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):

        if self.selected_option:
            self.question_status = 'answered'
            self.is_correct = self.selected_option.is_correct
            self.score = 1.0 if self.is_correct else 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.question.text} - {self.question.text[:30]}"