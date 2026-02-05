from django.urls import path
from apps.assessment_admin.views import Login
from apps.assessment_admin.views.UserAdministrationView import CreateUserView,UpdateUserView,ListUserView
from apps.assessment_admin.views.AssessmentView import CreateAssessmentView
from apps.assessment_admin.views.QuestionView import CreateQuestionView
from apps.assessment_admin.views.AssignAssessmentView import AssignAssessmentView
from apps.assessment_admin.views.ReportCandidateAssessment_View import ReportCandidateAssessmentView,ReportCandidateAssessmentDownloadView,ReportDownloadPDF
from apps.assessment_admin.views.ReportRawAssessment_View import ReportRawAssessmentView,ReportRawAssessmentDownloadView,ReportDownloadPDF as rawreportdownload
from apps.assessment_admin.views.AdminTasks import CreateEditLookupView

urlpatterns = [
    path('', Login.dashboard, name='admin-dashboard'),
    path('user/dashboard', Login.dashboard, name='admin-dashboard'),
    #User Profile URLS
    #path('admin/CreateUser', UserAdministrationView.CreateUser, name='admin-createuser'),
    path('assesspanel/CreateUser', CreateUserView.as_view(), name='admin-createuser'),
    path('assesspanel/UpdateUser', UpdateUserView.as_view(), name='admin-updateuser'),
    path('assesspanel/ListUser', ListUserView.as_view(), name='admin-listuser'),
    #Admin urls
    path('assesspanel/dropdownvalues', CreateEditLookupView.as_view(), name='admin-typelookupaddedit'),
    #Assessment URLS
    path('assessment/CreateEditAssessment', CreateAssessmentView.as_view(), name='assessment-createedit'),
    path('assessment/CreateEditQuestion', CreateQuestionView.as_view(), name='question-createedit'),
    path('assessment/AssignAssessment', AssignAssessmentView.as_view(), name='assessment-assigncandidate'),
    #Report URLS
    path('reports/candidateassessment', ReportCandidateAssessmentView.as_view(), name='report-candidateassessment'),
    path('reports/candidateassessmentView', ReportCandidateAssessmentDownloadView.as_view(), name='report-candidateassessmentview'),
    path("reports/candidateassessmentdownloadpdf", ReportDownloadPDF.as_view(), name="reportdownloadpdf"),
    path('reports/rawassessment', ReportRawAssessmentView.as_view(), name='report-rawassessment'),
    path('reports/rawassessmentView', ReportRawAssessmentDownloadView.as_view(), name='report-rawassessmentview'),
    path("reports/rawassessmentdownloadpdf", rawreportdownload.as_view(), name="reportrawdownloadpdf"),
    
]
