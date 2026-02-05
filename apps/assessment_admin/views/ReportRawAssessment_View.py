import json
from io import BytesIO

from django.contrib import messages
from django.core import signing
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from apps.assessment_admin.adminforms.assessment_form import (
    AssessmentCreateEditForm, AssessmentSearchForm)
from apps.assessment_admin.adminforms.rawassessmentreport_form import \
    RawAssessmentReportForm
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.assessment_service import AssessmentService
from apps.assessment_admin.services.useradministration_service import \
    useradministrationservice
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class ReportRawAssessmentView(View):
    template_name = "reports/rawassessmentreport.html"

    _rawassessform = RawAssessmentReportForm

    paginate_by = 15
    _assessmentservice = AssessmentService()
    _user_service = useradministrationservice()
    page_obj = None

    def get(self, request, *args, **kwargs):
        try:
            pass

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Raw Assessment Report",
            "rawassessreportform": self._rawassessform,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        post_form = self._rawassessform(request.POST)
        ActionName = request.POST.get("ActionName")

        try:
            ActionName = request.POST.get("ActionName")
            assessment_title = request.POST.get("title")
            assessment_language = request.POST.get("assessmentlanguage")
            if ActionName and ActionName == "searchassessment":
                filter_data = {}
                filter_data["srchtitle"] = assessment_title
                filter_data["srchlanguage"] = assessment_language
                filter_data["srchnum_of_questions"] = None
                assessment_list = self._assessmentservice.search_assessment(
                    filter_data, request.user
                )
                if assessment_list:
                    for assessment in assessment_list:
                        assessment.signed_id = signing.dumps(
                            {"id": assessment.id}, salt="assessment-salt"
                        )
                    paginator = Paginator(assessment_list, self.paginate_by)
                    page_number = request.POST.get("page", 1)
                    self.page_obj = paginator.get_page(page_number)

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Candidate Assessment Report",
            "rawassessreportform": post_form,
            "page_obj": self.page_obj,
        }
        return render(request, self.template_name, context)


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class ReportRawAssessmentDownloadView(View):
    template_name = "reports/viewrawassessment.html"

    _rawassessform = RawAssessmentReportForm

    paginate_by = 15
    _assessmentservice = AssessmentService()
    _user_service = useradministrationservice()
    page_obj = None
    current_assessment_candidateanswer = None

    def get(self, request, *args, **kwargs):
        current_assessment = None
        raw_assessment_data = []

        try:

            selected_assessmentid = request.GET.get("signed_id")
            selected_assessmentid_decoded = signing.loads(
                selected_assessmentid, salt="assessment-salt", max_age=28800
            )
            if selected_assessmentid_decoded:
                selected_assessmentid_decoded = selected_assessmentid_decoded["id"]
                current_assessment = self._assessmentservice.get_assessment_by_id(
                    selected_assessmentid_decoded
                )

                question_list = self._assessmentservice.read_question_by_assessment(
                    assessment=current_assessment
                )

                for question in question_list:
                    question_Ind_data = {}
                    question_Ind_data["question"] = question.text
                    question_Ind_data["options"] = question.options.all
                    question_Ind_data["correctoption"] = (
                        question.options.filter(is_correct=True).first().option_text
                    )

                    raw_assessment_data.append(question_Ind_data)

        except Exception as Ex:
            ViewError(
                message="CreateQuestionView: Failed on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "Raw Assessment Report",
            "rawassessreportform": self._rawassessform,
            "raw_assessment_data": raw_assessment_data,
            "current_assessment": current_assessment,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        post_form = self._rawassessform(request.POST)

        try:
            pass

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Candidate Assessment Report",
            "rawassessreportform": post_form,
            "page_obj": self.page_obj,
        }
        return render(request, self.template_name, context)


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class ReportDownloadPDF(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse JSON from JS
            data = json.loads(request.body)
            report_html = data.get("html", "")

            # Full HTML template for PDF, include inline styles
            html = f"""
            <html>
            <head>
                <style>
                body{{font-size:1rem;}}
                    .Question_p{{ font-weight:bold; font-size:1rem; color:#00095a; }}
                    .option_head{{ font-weight:bold; }}
                    .question_candidate_answer{{ font-weight:bold; color:#005de9; }}
                    .question_answer_status{{ font-weight:bold; color:#00095a; }}
                    .assessment_percentage{{ font-weight:bold; color:#dd0093; font-size:2rem; }}
                    .assessmenttitle,.assessmentdate,.assessmentlanguage,.candidatename,.candidatesite,.candidatescore{{ font-weight:bold; }}
                    .assessmenttitle span,.assessmentdate span,.assessmentlanguage span,.candidatename span,.candidatesite span,.candidatescore span{{ color: #ff6600; }}
                    .text-success {{color: #28a745 !important;}}.text-danger {{color: #dc3545 !important;}}
                </style>
            </head>
            <body>
                {report_html}
            </body>
            </html>
            """

            # Create PDF in memory
            result = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=result)

            if pisa_status.err:
                return HttpResponse("Error generating PDF", status=500)

            # Return PDF as response
            response = HttpResponse(result.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="report.pdf"'
            return response

        except Exception as Ex:
            ViewError(
                message="ReportDownloadPDF: Failed to generate PDF",
                original_exception=Ex,
                log=True,
            )
            return HttpResponse("Error generating PDF", status=500)
