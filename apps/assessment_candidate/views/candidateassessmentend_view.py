import random
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from apps.assessment_admin.decorators import role_required
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_CANDIDATE


@method_decorator(role_required([ROLE_CANDIDATE]), name="dispatch")
class CandidateAssessmentEndView(View):
    template_name = "candidate/AssessmentEnd.html"

    def get(self, request, *args, **kwargs):
        searched_username = None
        candidate_profile = None
        _searchform = None
        _assessment_start_continue = None
        page_obj = None
        try:
            pass

        except Exception as Ex:
            ViewError(
                message="AssignAssessmentView: Failed to get candidate data:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "An unexpected error occured")

        context = {"pagetitle": "Assessment Completed"}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class()
        page_obj = None
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
            "pagetitle": "Start Assessment",
            "AssessmentForm": form,
            "ProfileList": self.assessment_report_list,
            "page_obj": page_obj,
        }
        return render(request, self.template_name, context)
