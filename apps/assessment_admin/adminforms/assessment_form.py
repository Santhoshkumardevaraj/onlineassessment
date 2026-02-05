import re

import regex
from django import forms

from apps.assessment_admin.services.lookup_service import lookupservice
from apps.commonapp.exceptions.form_exceptions import FormError
from apps.commonapp.models import Assessment, Option, Question


class AssessmentCreateEditForm(forms.ModelForm):
    id = forms.CharField(
        max_length=100,
        widget=forms.HiddenInput(
            attrs={"id": "hdfipusername", "class": "form-control", "name": "id"}
        ),
    )
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "id": "txtbxtitle",
                "class": "form-control",
                "placeholder": "Title",
            }
        ),
        max_length=200,
        required=True,
    )
    description = forms.CharField(
        label="Description",
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "id": "txtbxdescription",
                "class": "form-control",
                "placeholder": "Description",
            }
        ),
        max_length=200,
        required=True,
    )
    language = forms.ChoiceField(
        label="Language",
        choices=[],
        widget=forms.Select(
            attrs={"id": "ddllanguage", "name": "Language", "class": "form-control"}
        ),
        required=True,
    )
    num_of_questions = forms.IntegerField(
        label="No of Questions",
        widget=forms.NumberInput(
            attrs={
                "id": "txtbxnofoquestions",
                "class": "form-control",
                "placeholder": "No of Questions",
                "min": "0",
                "max": "100",
            }
        ),
        required=True,
    )
    duration_minutes = forms.IntegerField(
        label="Duration in Minutes",
        widget=forms.NumberInput(
            attrs={
                "id": "txtbxdurationminutes",
                "class": "form-control",
                "placeholder": "Duration Minutes",
                "min": "1",
                "max": "120",
            }
        ),
        required=True,
    )

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "description",
            "language",
            "num_of_questions",
            "duration_minutes",
        ]

    def _validate_alphanumeric(self, fieldname, value):
        # Allowed letters for French, English, Spanish, Italian, Portuguese + numbers + basic punctuation
        ALLOWED_PATTERN = r"^[A-Za-z0-9ÀÁÂÃÄÅàáâãäåÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÇçÑñŸÿ\s,.\-!?\'_¿¡]+$"
        if not re.fullmatch(ALLOWED_PATTERN, value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={
                    "Error": fieldname + " must contain only alphanumeric characters."
                },
            )
            raise forms.ValidationError(
                "Invalid characters fpund: only letters, numbers, spaces and basic punctuation are allowed"
            )
        return value

    def _validate_numeric(self, fieldname, value):
        if not re.match(r"^[0-9\s]+$", value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={"Error": fieldname + " must contain only numeric characters."},
            )
            raise forms.ValidationError("Value must be Numeric")
        return value

    def clean_title(self):
        value = self.cleaned_data.get("title")
        value = self._validate_alphanumeric("Title", value)
        return value

    def clean_description(self):
        value = self.cleaned_data.get("description")
        if not value.strip():
            raise forms.ValidationError("Description Cannot be Empty")
        return value

    def clean_num_of_questions(self):
        value = self.cleaned_data.get("num_of_questions")
        if value < 1 or value > 100:
            raise forms.ValidationError("Value must be 1 to 100")
        return value

    def clean_duration_minutes(self):
        value = self.cleaned_data.get("duration_minutes")
        if value < 1 or value > 100:
            raise forms.ValidationError("Value must be 1 to 100")
        return value

    def __init__(self, *args, **kwargs):
        lookup_service = lookupservice()
        super().__init__(*args, **kwargs)
        field_map = {"language": "language"}

        for field_name, field_key in field_map.items():
            if field_name in self.fields:
                lookups = lookup_service.get_filtered_lookup(
                    datafield=field_key, datafor="all"
                ).order_by("dataparamvalue")

                self.fields[field_name].choices = [("", "--select--")] + [
                    (lookup.dataparamvalue, lookup.dataparamtext) for lookup in lookups
                ]


class AssessmentSearchForm(forms.Form):
    srchtitle = forms.CharField(
        label="Title",
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "id": "txtbxsrchtitle",
                "class": "form-control",
                "placeholder": "Title",
            }
        ),
        max_length=200,
        required=False,
    )
    srchlanguage = forms.ChoiceField(
        label="Language",
        choices=[],
        widget=forms.Select(
            attrs={"id": "ddlsrchlanguage", "name": "Language", "class": "form-control"}
        ),
        required=False,
    )
    srchnum_of_questions = forms.IntegerField(
        label="No of Questions",
        widget=forms.NumberInput(
            attrs={
                "id": "txtbxsrchnofoquestions",
                "class": "form-control",
                "placeholder": "No of Questions",
                "min": "0",
                "max": "100",
            }
        ),
        required=False,
    )

    def _validate_alphanumeric(self, fieldname, value):
        # Allowed letters for French, English, Spanish, Italian, Portuguese + numbers + basic punctuation
        ALLOWED_PATTERN = r"^[A-Za-z0-9ÀÁÂÃÄÅàáâãäåÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÇçÑñŸÿ\s,.\-!?\'_¿¡]+$"
        if not re.fullmatch(ALLOWED_PATTERN, value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={
                    "Error": fieldname + " must contain only alphanumeric characters."
                },
            )
            raise forms.ValidationError(
                "Invalid characters found: only letters, numbers, spaces and basic punctuation are allowed"
            )
        return value

    def _validate_numeric(self, fieldname, value):
        if not re.match(r"^[0-9\s]+$", value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={"Error": fieldname + " must contain only numeric characters."},
            )
            raise forms.ValidationError("Value must be Numeric")
        return value

    def clean_srchtitle(self):
        value = self.cleaned_data.get("srchtitle")
        if value:
            value = self._validate_alphanumeric("Title", value)
        return value

    def clean_srchnum_of_questions(self):
        value = self.cleaned_data.get("srchnum_of_questions")
        if value and (value < 1 or value > 100):
            raise forms.ValidationError("Value must be 1 to 100")
        return value

    def __init__(self, *args, **kwargs):
        lookup_service = lookupservice()
        super().__init__(*args, **kwargs)
        field_map = {"srchlanguage": "language"}

        for field_name, field_key in field_map.items():
            if field_name in self.fields:
                lookups = lookup_service.get_filtered_lookup(
                    datafield=field_key, datafor="all"
                ).order_by("dataparamvalue")

                self.fields[field_name].choices = [("", "--select--")] + [
                    (lookup.dataparamvalue, lookup.dataparamtext) for lookup in lookups
                ]


# Question

QUESTION_TYPE_CHOICES = (("MCQ", "Multiple Choice"),)


class QuestionCreateEditForm(forms.Form):
    question_id = forms.CharField(
        widget=forms.HiddenInput(
            attrs={"id": "HDFQuestionId", "name": "Questionrecordidforedit"}
        ),
        required=False,
    )
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        label="Question",
        required=True,
    )

    question_type = forms.ChoiceField(
        choices=QUESTION_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    option_1 = forms.CharField(
        label="Option 1",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,  # Mandatory
    )
    option_2 = forms.CharField(
        label="Option 2",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,  # Mandatory
    )
    option_3 = forms.CharField(
        label="Option 3",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    option_4 = forms.CharField(
        label="Option 4",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )

    correct_option = forms.ChoiceField(
        label="Correct Option",
        choices=[
            ("0", "Option 1"),
            ("1", "Option 2"),
            ("2", "Option 3"),
            ("3", "Option 4"),
        ],
        widget=forms.RadioSelect(attrs={"class": "custom-control-input"}),
        required=True,
    )

    def _validate_alphanumeric(self, fieldname, value):
        # Allowed letters for French, English, Spanish, Italian, Portuguese + numbers + basic punctuation
        ALLOWED_PATTERN = r"^[A-Za-z0-9ÀÁÂÃÄÅàáâãäåÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÇçÑñŸÿ\s,.\-!?\'_¿¡]+$"
        if not re.fullmatch(ALLOWED_PATTERN, value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={
                    "Error": fieldname + " must contain only alphanumeric characters."
                },
            )
            raise forms.ValidationError(
                "Invalid characters found: only letters, numbers, spaces and basic punctuation are allowed"
            )
        return value

    def clean_question_text(self):
        value = self.cleaned_data.get("question_text")
        if value:
            value = self._validate_alphanumeric("question_text", value)
        return value

    def clean_option_1(self):
        value = self.cleaned_data.get("option_1")
        if value:
            value = self._validate_alphanumeric("option_1", value)
        return value

    def clean_option_2(self):
        value = self.cleaned_data.get("option_2")
        if value:
            value = self._validate_alphanumeric("option_2", value)
        return value

    def clean_option_3(self):
        value = self.cleaned_data.get("option_3")
        if value:
            value = self._validate_alphanumeric("option_3", value)
        return value

    def clean_option_4(self):
        value = self.cleaned_data.get("option_4")
        if value:
            value = self._validate_alphanumeric("option_4", value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        correct_option = cleaned_data.get("correct_option")

        # Get option texts
        options = [
            cleaned_data.get("option_1"),
            cleaned_data.get("option_2"),
            cleaned_data.get("option_3"),
            cleaned_data.get("option_4"),
        ]

        # Ensure selected correct_option corresponds to a non-empty option
        if correct_option is not None:
            index = int(correct_option)
            selected_text = options[index]
            if not selected_text or selected_text.strip() == "":
                self.add_error(
                    "correct_option", "The selected correct option cannot be empty."
                )

        # Ensure at least first two options are filled (redundant if required=True)
        if not cleaned_data.get("option_1"):
            self.add_error("option_1", "Option 1 is required.")
        if not cleaned_data.get("option_2"):
            self.add_error("option_2", "Option 2 is required.")
