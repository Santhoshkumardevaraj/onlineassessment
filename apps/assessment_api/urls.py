from django.urls import path

from apps.assessment_api.views.candidateanswerapi_view import (
    CandidateAnswer_OptionView, CandidateAnswer_questionView,
    CandidateAnswerView, CandidateEndAssessmentView)
from apps.assessment_api.views.UserProfileApi import (CandidateProfileView,
                                                      DefaultView,
                                                      UserProfileView)

urlpatterns = [
    path("", DefaultView.as_view(), name="API_Default"),
    path("UserprofileLoginidList", UserProfileView.as_view(), name="API_userprofile"),
    path(
        "CandidateprofileLoginidList",
        CandidateProfileView.as_view(),
        name="API_candidateprofile",
    ),
    path(
        "CandidateAssessmentQuestlist",
        CandidateAnswerView.as_view(),
        name="API_candidateassessmentquestionlist",
    ),
    path(
        "CandidateAssessmentCurrentQuestion",
        CandidateAnswer_questionView.as_view(),
        name="API_candidateassessmentcurrentquestion",
    ),
    path(
        "CandidateAnswerOption",
        CandidateAnswer_OptionView.as_view(),
        name="API_candidateansweroption",
    ),
    path(
        "CandidateEndAssessment",
        CandidateEndAssessmentView.as_view(),
        name="API_candidateendassessment",
    ),
]
