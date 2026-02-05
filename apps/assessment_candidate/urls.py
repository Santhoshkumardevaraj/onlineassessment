from django.urls import path
from .views import candidatestartassessment_view,candidatewriteassessment_view,candidateassessmentend_view

urlpatterns = [
    path('candidate/startassessment', candidatestartassessment_view.CandidateStartAssessmentView.as_view(), name='candidate-AssessmentStart'),
    path('', candidatestartassessment_view.CandidateStartAssessmentView.as_view(), name='candidate-AssessmentStart'),
    path('candidate/writeassessment', candidatewriteassessment_view.CandidateWriteAssessment.as_view(), name='candidate-AssessmentWrite'),
    path('candidate/assessmentend', candidateassessmentend_view.CandidateAssessmentEndView.as_view(), name='candidate-AssessmentEnd'),
]