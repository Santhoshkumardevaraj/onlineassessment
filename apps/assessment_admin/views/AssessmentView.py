from django.contrib import messages
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from apps.assessment_admin.adminforms.assessment_form import (
    AssessmentCreateEditForm, AssessmentSearchForm)
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.assessment_service import AssessmentService
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class CreateAssessmentView(View):
    template_name = "assessment/addeditassessment.html"
    form_class = AssessmentCreateEditForm
    search_form = AssessmentSearchForm
    paginate_by = 15
    _service = AssessmentService()
    form_current_action = None
    form_card_class = None
    form_card_title = None
    assessment_report_list = None

    def get(self, request, *args, **kwargs):
        try:
            _assessmentform = self.form_class(initial={"id": 0})
            _searchform = self.search_form()
            self.assessment_report_list = self._service.read_recent_assessment()
            page_obj = None
            ActionName = request.GET.get("ActionName")
            # print(ActionName)
            self.form_card_class = "card-primary"
            self.form_card_title = "Assessment Creation"

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
                message="CreateAssessmentView: Failed on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "Create Assessment",
            "AssessmentForm": _assessmentform,
            "AssessmentSearchForm": _searchform,
            "AssessmentList": self.assessment_report_list,
            "page_obj": page_obj,
            "form_card_class": self.form_card_class,
            "form_card_title": self.form_card_title,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class()
        page_obj = None
        _searchform = self.search_form()
        ActionName = request.POST.get("ActionName")
        selected_recordid_decoded = 0

        if ActionName and ActionName == "editassessment":
            try:
                selected_recordid = request.POST.get("assessmentidforaction")
                selected_recordid_decoded = signing.loads(
                    selected_recordid, salt="assessment-salt", max_age=3600
                )
                if selected_recordid_decoded:
                    selected_recordid_decoded = selected_recordid_decoded["id"]

                assessment = self._service.get_assessment_by_id(
                    recordid=selected_recordid_decoded
                )
                if assessment:
                    form = self.form_class(instance=assessment)
                    self.form_current_action = "UpdateAssessment"
                    self.form_card_class = "card-success"
                    self.form_card_title = "Assessment Update"
                else:
                    messages.error(request, "Requested Data Nod Found")
            except Exception as Ex:
                ViewError(
                    message="CreateAssessmentView: Failed to edit assessment:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Page Error Please Escalate")
        elif ActionName and ActionName == "updateassessment":
            form = self.form_class(request.POST)
            if form.is_valid():
                try:
                    updated_assessment_data = form.cleaned_data
                    if updated_assessment_data:
                        assessment = self._service.update_assessment(
                            form.cleaned_data, currentuser=request.user
                        )
                        if assessment:
                            form = self.form_class(instance=assessment)
                            self.form_current_action = "UpdateAssessment"
                            messages.success(request, "Assessment Updated Successfully")
                            self.form_card_class = "card-success"
                            self.form_card_title = "Assessment Update"
                    else:
                        messages.error(request, "Requested Data Nod Found")
                    # print(updated_assessment_data)
                except Exception as Ex:
                    ViewError(
                        message="CreateAssessmentView: Failed to update assessment:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "Data Save Failed")
            else:
                errordetails = {"formerror": form.errors.as_json()}
                ViewError(
                    message="CreateAssessmentView: Form Validation Failed:",
                    original_exception=None,
                    extra=errordetails,
                    log=True,
                )
                messages.error(request, "Invalid or Incomplete data filled")
        elif ActionName and ActionName == "deleteassessment":
            selected_recordid = request.POST.get("assessmentidforaction")
            selected_recordid_decoded = signing.loads(
                selected_recordid, salt="assessment-salt", max_age=3600
            )
            if selected_recordid_decoded:
                selected_recordid_decoded = selected_recordid_decoded["id"]

            try:
                delete_assessment = self._service.get_assessment_by_id(
                    recordid=selected_recordid_decoded
                )
                if delete_assessment:
                    assessment = self._service.update_assessment_remove(
                        delete_assessment, currentuser=request.user
                    )
                    if assessment:
                        messages.success(request, "Assessment Deleted Successfully")
                else:
                    messages.error(request, "Requested Data Nod Found")
                # print(updated_assessment_data)
            except Exception as Ex:
                ViewError(
                    message="CreateAssessmentView: Failed to delete assessment:",
                    original_exception=Ex,
                    extra=None,
                    log=True,
                )
                messages.error(request, "Data Save Failed")

        elif ActionName and ActionName == "saveassessment":
            form = self.form_class(request.POST)
            if form.is_valid():
                try:
                    assessment = self._service.create_assessment(
                        form.cleaned_data, currentuser=request.user
                    )
                    if assessment:
                        messages.success(request, "Assessment Created Successfully")
                        return redirect("assessment-createedit")
                    else:
                        messages.error(request, "Data Save Failed")
                except Exception as Ex:
                    ViewError(
                        message="CreateAssessmentView: Failed to save assessment:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "Data Save Failed")
            else:
                errordetails = {"formerror": form.errors.as_json()}
                ViewError(
                    message="CreateAssessmentView: Form Validation Failed:",
                    original_exception=None,
                    extra=errordetails,
                    log=True,
                )
                messages.error(request, "Invalid or Incomplete data filled")

        elif ActionName and ActionName == "searchassessment":
            form = self.search_form(request.POST)
            if form.is_valid():
                try:
                    self.assessment_report_list = self._service.search_assessment(
                        form.cleaned_data, currentuser=request.user
                    )
                    if not self.assessment_report_list:
                        messages.error(request, "No Data Found")
                except Exception as Ex:
                    ViewError(
                        message="CreateAssessmentView: Failed to search assessment:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "No Data Found")
            else:
                errordetails = {"formerror": form.errors.as_json()}
                ViewError(
                    message="CreateAssessmentView: Form Validation Failed:",
                    original_exception=None,
                    extra=errordetails,
                    log=True,
                )
                messages.error(request, "Invalid or Incomplete data filled")
        # Code to redirect control to QUESTION add or edit page
        elif ActionName and ActionName == "addquestion":
            question_edit_assessment = self._service.get_assessment_by_id(
                recordid=selected_recordid_decoded
            )

            try:
                if question_edit_assessment:
                    return redirect("question-createedit")
                else:
                    messages.error(request, "Requested Data Nod Found")
            except Exception as Ex:
                ViewError(
                    message="CreateAssessmentView: Failed to add question:",
                    original_exception=Ex,
                    extra=None,
                    log=True,
                )
                messages.error(request, "Data Save Failed")

        # On error, re-render the same page with form and list
        if not self.assessment_report_list:
            self.assessment_report_list = self._service.read_recent_assessment()
        if self.assessment_report_list:

            for assessment in self.assessment_report_list:
                assessment.signed_id = signing.dumps(
                    {"id": assessment.id}, salt="assessment-salt"
                )
            paginator = Paginator(self.assessment_report_list, self.paginate_by)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

        context = {
            "pagetitle": "Create Assessment",
            "AssessmentForm": form,
            "AssessmentSearchForm": _searchform,
            "ProfileList": self.assessment_report_list,
            "page_obj": page_obj,
            "form_current_action": self.form_current_action,
            "form_card_class": self.form_card_class,
            "form_card_title": self.form_card_title,
        }
        return render(request, self.template_name, context)
