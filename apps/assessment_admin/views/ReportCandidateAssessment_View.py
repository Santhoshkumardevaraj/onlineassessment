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
from apps.assessment_admin.adminforms.candidateassessmentreport_form import \
    CandidateAssessmentReportForm
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.assessment_service import AssessmentService
from apps.assessment_admin.services.assessmentassign_service import \
    AssessmentAssignService
from apps.assessment_admin.services.useradministration_service import \
    useradministrationservice
from apps.assessment_candidate.services.candidateanswer_service import \
    CandidateAnswerService
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class ReportCandidateAssessmentView(View):
    template_name = "reports/candidateassessmentreport.html"

    _candassessform = CandidateAssessmentReportForm

    paginate_by = 15
    _assessmentservice = AssessmentService()
    _assessmentassignservice = AssessmentAssignService()
    _user_service = useradministrationservice()
    page_obj = None

    def get(self, request, *args, **kwargs):
        searched_username = None
        candidate_profile = None
        _searchform = None

        try:

            ActionName = request.GET.get("ActionName")
            cand_loginid = request.GET.get("username")
            if ActionName and ActionName == "removeassessmentconduct":
                selected_recordid = request.GET.get("assessmentconductidforaction")
                selected_recordid_decoded = signing.loads(
                    selected_recordid, salt="assessmentconduct-salt", max_age=3600
                )

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Candidate Assessment Report",
            "candassessreportform": self._candassessform,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        post_form = self._candassessform(request.POST)
        ActionName = request.POST.get("ActionName")
        selected_recordid_decoded = 0
        searched_username = None
        candidate_profile = None

        try:
            assessment_fromdate = request.POST.get("assessment_fromdate")
            assessment_lastdate = request.POST.get("assessment_tillate")
            assessment_assessmenttitle = request.POST.get("title")
            assessment_assessmentlanguage = request.POST.get("assessmentlanguage")
            candidate_site = request.POST.get("candidatesite")
            candidate_language = request.POST.get("candidatelanguage")
            candidate_firstname = request.POST.get("candidatefirstname")
            candidate_lastname = request.POST.get("candidatelastname")
            candidate_mailid = request.POST.get("candidateemailid")

            if assessment_fromdate and assessment_lastdate:
                assessmentconducted_list = (
                    self._assessmentassignservice.get_assessmentconduct_by_filter(
                        assessment_fromdate=assessment_fromdate,
                        assessment_lastdate=assessment_lastdate,
                        assessment_assessmenttitle=assessment_assessmenttitle,
                        assessment_assessmentlanguage=assessment_assessmentlanguage,
                        candidate_site=candidate_site,
                        candidate_language=candidate_language,
                        candidate_firstname=candidate_firstname,
                        candidate_lastname=candidate_lastname,
                        candidate_mailid=candidate_mailid,
                    )
                )
                if assessmentconducted_list:
                    for assessmentconduct in assessmentconducted_list:
                        total = assessmentconduct.candidate_answers.count()
                        correct = assessmentconduct.candidate_answers.filter(
                            score=1.0
                        ).count()
                        percentage = round((correct / total) * 100) if total > 0 else 0
                        assessmentconduct.score = percentage
                        assessmentconduct.signed_id = signing.dumps(
                            {"id": assessmentconduct.id}, salt="assessmentconduct-salt"
                        )
                    paginator = Paginator(assessmentconducted_list, self.paginate_by)
                    page_number = request.GET.get("page", 1)
                    self.page_obj = paginator.get_page(page_number)

            if ActionName and ActionName == "removeassessmentconduct":
                selected_recordid = request.POST.get("assessmentconductidforaction")
                if selected_recordid:
                    selected_recordid_decoded = signing.loads(
                        selected_recordid, salt="assessmentconduct-salt", max_age=3600
                    )
                    if selected_recordid_decoded:
                        selected_recordid_decoded = selected_recordid_decoded["id"]
                        assessment_conduct_toremove = (
                            self._assessmentassignservice.get_assessmentconduct_by_id(
                                selected_recordid_decoded
                            )
                        )
                        if assessment_conduct_toremove:
                            remove_assessmentconduct = self._assessmentassignservice.update_assessmentconduct_remove(
                                assessment_conduct=assessment_conduct_toremove,
                                currentuser=request.user,
                            )
                            if remove_assessmentconduct:
                                messages.success(
                                    request, "Assessment removed successfully"
                                )
                            else:
                                messages.error(request, "Assessment remove failed")

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Candidate Assessment Report",
            "candassessreportform": post_form,
            "page_obj": self.page_obj,
        }
        return render(request, self.template_name, context)


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class ReportCandidateAssessmentDownloadView(View):
    template_name = "reports/viewcandidateassessment.html"

    _candassessform = CandidateAssessmentReportForm

    paginate_by = 15
    _assessmentservice = AssessmentService()
    _assessmentassignservice = AssessmentAssignService()
    _candidateanswerservice = CandidateAnswerService()
    _user_service = useradministrationservice()
    page_obj = None
    current_assessment_candidateanswer = None

    def get(self, request, *args, **kwargs):
        searched_username = None
        candidate_profile = None
        _searchform = None
        assessment_percentage = None
        current_assessmentconduct = None
        candidate_assessment_data = []

        try:

            selected_assessmentconductid = request.GET.get("signed_id")
            selected_assessmentconductid_decoded = signing.loads(
                selected_assessmentconductid,
                salt="assessmentconduct-salt",
                max_age=28800,
            )
            if selected_assessmentconductid_decoded:
                selected_assessmentconductid_decoded = (
                    selected_assessmentconductid_decoded["id"]
                )
                current_assessmentconduct = (
                    self._assessmentassignservice.get_assessmentconduct_by_id(
                        recordid=selected_assessmentconductid_decoded
                    )
                )
                self.current_assessment_candidateanswer = (
                    self._candidateanswerservice.read_candidate_questions(
                        current_assessmentconduct.id
                    )
                )

                total = current_assessmentconduct.candidate_answers.count()
                correct = current_assessmentconduct.candidate_answers.filter(
                    score=1.0
                ).count()
                assessment_percentage = (
                    round((correct / total) * 100) if total > 0 else 0
                )

                for cand_answer in self.current_assessment_candidateanswer:
                    candidate_Ind_data = {}
                    candidate_Ind_data["question"] = cand_answer.question.text
                    candidate_Ind_data["options"] = cand_answer.question.options.all
                    cand_opt = None
                    if cand_answer.selected_option:
                        cand_opt = cand_answer.question.options.filter(
                            id=getattr(cand_answer.selected_option, "id")
                        ).first()
                    candidate_Ind_data["candidateoption"] = (
                        cand_opt.option_text if cand_opt else None
                    )
                    candidate_Ind_data["answerstatus"] = None
                    if cand_opt:
                        if (
                            cand_opt.id
                            == cand_answer.question.options.filter(is_correct=True)
                            .first()
                            .id
                        ):
                            candidate_Ind_data["answerstatus"] = "correct"
                        else:
                            candidate_Ind_data["answerstatus"] = "wrong"

                    candidate_assessment_data.append(candidate_Ind_data)

        except Exception as Ex:
            ViewError(
                message="CreateQuestionView: Failed on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "Candidate Assessment Report",
            "candassessreportform": self._candassessform,
            "current_assessment_candidateanswer": candidate_assessment_data,
            "assessment_percentage": assessment_percentage,
            "current_assessmentconduct": current_assessmentconduct,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        post_form = self._candassessform(request.POST)
        ActionName = request.POST.get("ActionName")
        selected_recordid_decoded = 0
        searched_username = None
        candidate_profile = None

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
            "candassessreportform": post_form,
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
