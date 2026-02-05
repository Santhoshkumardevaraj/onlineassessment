import random
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from apps.assessment_admin.adminforms.assessment_form import (
    AssessmentCreateEditForm, AssessmentSearchForm)
from apps.assessment_admin.decorators import role_required
from apps.assessment_candidate.services.assessment_service import \
    AssessmentService
from apps.assessment_candidate.services.assessmentassign_service import \
    AssessmentAssignService
from apps.assessment_candidate.services.candidateanswer_service import \
    CandidateAnswerService
from apps.assessment_candidate.services.useradministration_service import \
    useradministrationservice
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_CANDIDATE


@method_decorator(role_required([ROLE_CANDIDATE]), name="dispatch")
class CandidateStartAssessmentView(View):
    template_name = "candidate/AssessmentStart.html"
    form_class = AssessmentCreateEditForm
    search_form = AssessmentSearchForm
    paginate_by = 15
    _assessmentservice = AssessmentService()
    _assessmentassignservice = AssessmentAssignService()
    _user_service = useradministrationservice()
    _candidateanswer = CandidateAnswerService()
    form_current_action = None
    form_card_class = None
    form_card_title = None
    assessment_report_list = None
    assigned_assessment = None

    def get_assessments_assigned_for_candidate(self, candidate_profile, currentuser):
        self.assigned_assessment = (
            self._assessmentassignservice.check_assessmentconduct(
                candidate=candidate_profile,
                assessment=None,
                assessment_date=None,
                currentuser=currentuser,
            ).first()
        )

        if self.assigned_assessment:
            self.assigned_assessment.signed_id = signing.dumps(
                {"id": self.assigned_assessment.id}, salt="assessmentconduct-salt"
            )
        else:
            self.assigned_assessment = None

    def get(self, request, *args, **kwargs):
        searched_username = None
        candidate_profile = None
        _searchform = None
        _assessment_start_continue = None
        page_obj = None
        try:
            cand_loginid = request.user.username
            yesterday_Date = date.today() - timedelta(days=1)
            assessmentdateframe = yesterday_Date.strftime("%Y-%m-%d")
            if cand_loginid and cand_loginid != "":
                candidate_profile = self._user_service.get_user_list_filtered(
                    loginid=cand_loginid
                ).first()
                if candidate_profile and candidate_profile.username:
                    self.get_assessments_assigned_for_candidate(
                        candidate_profile, request.user
                    )
                    searched_username = candidate_profile.username

                    _searchform = self.search_form()

                    if (
                        self.assigned_assessment
                        and self.assigned_assessment.assessment_start_datetime
                    ):
                        _assessment_start_continue = "continue"
                    else:
                        _assessment_start_continue = "start"

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Assign Assessment",
            "AssessmentSearchForm": _searchform,
            "page_obj": page_obj,
            "form_card_class": self.form_card_class,
            "form_card_title": self.form_card_title,
            "searched_username": searched_username,
            "candidate_profile": candidate_profile,
            "assigned_assessment": self.assigned_assessment,
            "assessment_start_continue": _assessment_start_continue,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class()
        page_obj = None
        _searchform = self.search_form()
        ActionName = request.POST.get("ActionName")
        selected_recordid_decoded = 0
        searched_username = None
        candidate_profile = None

        try:
            cand_loginid = request.user.username
            yesterday_Date = date.today() - timedelta(days=1)
            assessmentdateframe = yesterday_Date.strftime("%Y-%m-%d")
            if cand_loginid and cand_loginid != "":
                candidate_profile = self._user_service.get_user_list_filtered(
                    loginid=cand_loginid
                ).first()
                if candidate_profile and candidate_profile.username:
                    self.get_assessments_assigned_for_candidate(
                        candidate_profile, request.user
                    )
                    searched_username = candidate_profile.username

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        if ActionName and ActionName == "startassessment":
            try:
                if self.assigned_assessment and self.assigned_assessment.assessment:
                    all_questions = list(
                        self.assigned_assessment.assessment.questions.filter(
                            active=True
                        )
                    )
                    total_question_count = len(all_questions)
                    questions_tobegenerated_assessment = (
                        self.assigned_assessment.assessment.num_of_questions
                    )

                    if total_question_count > 0:
                        num_to_pick = min(
                            questions_tobegenerated_assessment, total_question_count
                        )
                        questions_to_be_assigned = random.sample(
                            all_questions, num_to_pick
                        )
                        if questions_to_be_assigned:
                            add_candidatequestions = (
                                self._candidateanswer.create_candidateanswer(
                                    candidate=candidate_profile,
                                    assessment=self.assigned_assessment.assessment,
                                    assessmentconduct=self.assigned_assessment,
                                    questions=questions_to_be_assigned,
                                    currentuser=request.user,
                                )
                            )
                            if add_candidatequestions:
                                return redirect("candidate-AssessmentWrite")

                    else:
                        messages.error(request, "No questions to fetch from assessment")
                else:
                    messages.error(request, "No assessment assigned")
            except Exception as Ex:
                ViewError(
                    message="StartAssessmentView: Failed to edit assessment:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Page Error Please Escalate")

        elif ActionName and ActionName == "continueassessment":
            try:
                if self.assigned_assessment and self.assigned_assessment.assessment:
                    all_questions = list(
                        self.assigned_assessment.assessment.questions.filter(
                            active=True
                        )
                    )
                    total_question_count = len(all_questions)

                    if total_question_count > 0:
                        return redirect("candidate-AssessmentWrite")

                    else:
                        messages.error(request, "No questions to fetch from assessment")
                else:
                    messages.error(request, "No assessment assigned")
            except Exception as Ex:
                ViewError(
                    message="StartAssessmentView: Failed to edit assessment:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Page Error Please Escalate")

        try:
            if candidate_profile and candidate_profile.username:
                searched_username = candidate_profile.username
                self.get_assessments_assigned_for_candidate(
                    candidate_profile, request.user
                )

                # On error, re-render the same page with form and list
                if not self.assessment_report_list:
                    self.assessment_report_list = (
                        self._assessmentservice.read_recent_assessment()
                    )
                if self.assessment_report_list:

                    for assessment in self.assessment_report_list:
                        assessment.signed_id = signing.dumps(
                            {"id": assessment.id}, salt="assessment-salt"
                        )
                    paginator = Paginator(self.assessment_report_list, self.paginate_by)
                    page_number = request.GET.get("page")
                    page_obj = paginator.get_page(page_number)

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {
            "pagetitle": "Start Assessment",
            "AssessmentForm": form,
            "searched_username": searched_username,
            "candidate_profile": candidate_profile,
            "assigned_assessment": self.assigned_assessment,
            "AssessmentSearchForm": _searchform,
            "ProfileList": self.assessment_report_list,
            "page_obj": page_obj,
        }
        return render(request, self.template_name, context)
