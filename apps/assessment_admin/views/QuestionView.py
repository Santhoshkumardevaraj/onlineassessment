from urllib.parse import urlencode

from django.contrib import messages
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from apps.assessment_admin.adminforms.assessment_form import (
    AssessmentSearchForm, QuestionCreateEditForm)
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.assessment_service import AssessmentService
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class CreateQuestionView(View):
    template_name = "assessment/addeditquestion.html"
    form_class = QuestionCreateEditForm
    search_form = AssessmentSearchForm
    paginate_by = 15
    _service = AssessmentService()
    form_current_action = None
    form_card_class = None
    form_card_title = None
    Question_report_list = None

    def log_form_failure(self, form):
        errordetails = {"formerror": form.errors.as_json()}
        ViewError(
            message="CreateQuestionView: Form Validation Failed:",
            original_exception=None,
            extra=errordetails,
            log=True,
        )

    def get(self, request, *args, **kwargs):
        _QuestionCreateform = self.form_class(initial={"id": 0})

        page_obj = None
        selected_assessmentid_decoded = 0
        # print(ActionName)
        try:
            self.form_card_class = "card-primary"
            self.form_card_title = "Question Add"
            selected_assessmentid = request.GET.get("signed_id")
            selected_assessmentid_decoded = signing.loads(
                selected_assessmentid, salt="assessment-salt", max_age=28800
            )
            if selected_assessmentid_decoded:
                selected_assessmentid_decoded = selected_assessmentid_decoded["id"]
            current_assessment = self._service.get_assessment_by_id(
                recordid=selected_assessmentid_decoded
            )
            self.Question_report_list = self._service.read_question_by_assessment(
                assessment=current_assessment
            )
            if self.Question_report_list:
                for question in self.Question_report_list:
                    question.signed_id = signing.dumps(
                        {"id": question.id}, salt="assessment-salt"
                    )
                paginator = Paginator(self.Question_report_list, self.paginate_by)
                page_number = request.GET.get("page", 1)
                page_obj = paginator.get_page(page_number)

        except Exception as Ex:
            ViewError(
                message="CreateQuestionView: Failed on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "Add/Edit Question",
            "current_assessment": current_assessment,
            "CreateQuestionForm": _QuestionCreateform,
            "page_obj": page_obj,
            "form_card_class": self.form_card_class,
            "form_card_title": self.form_card_title,
            "signed_id": selected_assessmentid,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class()
        page_obj = None
        _QuestionCreateform = self.form_class(initial={"id": 0})
        _searchform = self.search_form()
        ActionName = request.POST.get("ActionName")
        selected_assessmentid_decoded = 0
        selected_assessmentid = request.GET.get("signed_id")
        selected_assessmentid_decoded = signing.loads(
            selected_assessmentid, salt="assessment-salt", max_age=28800
        )
        base_url = reverse("question-createedit")
        query_string = urlencode({"signed_id": selected_assessmentid})
        return_url_with_id = f"{base_url}?{query_string}"

        if selected_assessmentid_decoded:
            selected_assessmentid_decoded = selected_assessmentid_decoded["id"]
        current_assessment = self._service.get_assessment_by_id(
            recordid=selected_assessmentid_decoded
        )
        if current_assessment:
            self.Question_report_list = self._service.read_question_by_assessment(
                assessment=current_assessment
            )
            if ActionName and ActionName == "editquestion":
                try:
                    selected_questionid = request.POST.get("questionidforaction")
                    selected_questionid_decoded = signing.loads(
                        selected_questionid, salt="assessment-salt", max_age=28800
                    )
                    _question = self._service.get_question_by_id(
                        recordid=selected_questionid_decoded["id"]
                    )
                    if _question:
                        _option_list = _question.options.all()
                        correct_index = None
                        for i, option in enumerate(_option_list[:4]):
                            if option.is_correct:
                                correct_index = str(i)
                                break

                        _QuestionCreateform = self.form_class(
                            initial={
                                "question_id": selected_questionid,
                                "question_text": _question.text,
                                "question_type": _question.question_type,
                                "option_1": _option_list[0].option_text,
                                "option_2": _option_list[1].option_text,
                                "option_3": _option_list[2].option_text,
                                "option_4": _option_list[3].option_text,
                                "correct_option": correct_index,
                            }
                        )
                        self.form_current_action = "UpdateQuestion"
                        self.form_card_class = "card-success"
                        self.form_card_title = "Question Update"
                    else:
                        messages.error(request, "Requested Data Not Found")
                except Exception as Ex:
                    ViewError(
                        message="CreateQuestionView: Failed to update question:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "Data Fetch Failed")
            elif ActionName and ActionName == "updatequestion":
                form = self.form_class(request.POST)
                if form.is_valid():
                    try:
                        updated_assessment_data = form.cleaned_data
                        selected_questionid = request.POST.get("question_id")
                        selected_questionid_decoded = signing.loads(
                            selected_questionid, salt="assessment-salt", max_age=28800
                        )
                        _question = self._service.get_question_by_id(
                            recordid=selected_questionid_decoded["id"]
                        )
                        if _question:
                            form.cleaned_data["question_id"] = (
                                selected_questionid_decoded["id"]
                            )
                            question_result = self._service.update_question_and_options(
                                form.cleaned_data, _question, currentuser=request.user
                            )
                            if question_result:
                                _option_list = question_result.options.all()
                                correct_index = None
                                for i, option in enumerate(_option_list[:4]):
                                    if option.is_correct:
                                        correct_index = str(i)
                                        break
                                _QuestionCreateform = self.form_class(
                                    initial={
                                        "question_id": selected_questionid,
                                        "question_text": question_result.text,
                                        "question_type": question_result.question_type,
                                        "option_1": _option_list[0].option_text,
                                        "option_2": _option_list[1].option_text,
                                        "option_3": _option_list[2].option_text,
                                        "option_4": _option_list[3].option_text,
                                        "correct_option": correct_index,
                                    }
                                )
                                self.form_current_action = "UpdateQuestion"
                                messages.success(
                                    request, "Question Updated Successfully"
                                )
                                self.form_card_class = "card-success"
                                self.form_card_title = "Question Update"
                        else:
                            messages.error(request, "Requested Data Nod Found")
                        # print(updated_assessment_data)
                    except Exception as Ex:
                        ViewError(
                            message="CreateQuestionView: Failed to update question:",
                            original_exception=Ex,
                            extra=None,
                            log=True,
                        )
                        messages.error(request, "Data update failed")
                else:
                    self.log_form_failure(form)
                    messages.error(request, "Invalid or Incomplete data filled")
            elif ActionName and ActionName == "deletequestion":
                selected_questionid = request.POST.get("questionidforaction")
                selected_questionid_decoded = signing.loads(
                    selected_questionid, salt="assessment-salt", max_age=28800
                )
                delete_question = self._service.get_question_by_id(
                    recordid=selected_questionid_decoded["id"]
                )

                try:
                    if delete_question:
                        delete_status = self._service.update_question_remove(
                            delete_question, currentuser=request.user
                        )
                        if delete_status:
                            messages.success(request, "Question Deleted Successfully")
                            return redirect(return_url_with_id)
                    else:
                        messages.error(request, "Requested Data Nod Found")
                    # print(updated_assessment_data)
                except Exception as Ex:
                    ViewError(
                        message="CreateQuestionView: Failed to delete question:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "Data delete Failed")

            elif ActionName and ActionName == "savequestion":
                form = self.form_class(request.POST)
                if form.is_valid():
                    try:
                        assessment = self._service.create_question(
                            curr_assessment=current_assessment,
                            cleaned_data=form.cleaned_data,
                            currentuser=request.user,
                        )
                        if assessment:
                            messages.success(request, "Question Created Successfully")
                            return redirect(return_url_with_id)
                        else:
                            messages.error(request, "Data Save Failed")
                    except Exception as Ex:
                        ViewError(
                            message="CreateQuestionView: Failed to save question:",
                            original_exception=Ex,
                            extra=None,
                            log=True,
                        )
                        messages.error(request, "Data Save Failed")
                else:
                    self.log_form_failure(form)
                    messages.error(request, "Invalid or Incomplete data filled")

            elif ActionName and ActionName == "searchquestion":
                form = self.search_form(request.POST)
                srch_text = request.POST.get("srchquestionhint")
                if srch_text:
                    try:
                        self.Question_report_list = (
                            self._service.search_question_bytext(
                                assessment=current_assessment, srchtext=srch_text
                            )
                        )
                        if not self.Question_report_list:
                            messages.warning(request, "No Data Found")
                    except Exception as Ex:
                        ViewError(
                            message="CreateQuestionView: Failed to search question:",
                            original_exception=Ex,
                            extra=None,
                            log=True,
                        )
                        messages.error(request, "No Data Found")
                else:
                    messages.warning(request, "No Records Found")

            elif ActionName and ActionName == "resetpage":
                form = self.form_class(request.POST)
                if form.is_valid():
                    try:
                        return redirect(return_url_with_id)
                    except Exception as Ex:
                        ViewError(
                            message="CreateQuestionView: Failed to reset page:",
                            original_exception=Ex,
                            extra=None,
                            log=True,
                        )
                        messages.error(request, "page error")
                else:
                    self.log_form_failure(form)
                    messages.error(request, "Invalid or Incomplete data filled")

        # On error, re-render the same page with form and list

        if self.Question_report_list:
            for question in self.Question_report_list:
                question.signed_id = signing.dumps(
                    {"id": question.id}, salt="assessment-salt"
                )
            paginator = Paginator(self.Question_report_list, self.paginate_by)
            page_number = request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)

        context = {
            "pagetitle": "Add/Edit Question",
            "current_assessment": current_assessment,
            "CreateQuestionForm": _QuestionCreateform,
            "QuestionSearchForm": _searchform,
            "ProfileList": self.Question_report_list,
            "page_obj": page_obj,
            "form_current_action": self.form_current_action,
            "form_card_class": self.form_card_class,
            "form_card_title": self.form_card_title,
            "signed_id": selected_assessmentid,
        }
        return render(request, self.template_name, context)
