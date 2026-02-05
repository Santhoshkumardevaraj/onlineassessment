import re

from django import forms
from django.contrib import messages

from apps.commonapp.exceptions.form_exceptions import FormError
from apps.commonapp.models.TypeLookupModel import TypeLookup


class TypeLookupForm(forms.ModelForm):
    class Meta:
        model = TypeLookup
        fields = ["datafield", "datafor", "dataparamtext", "dataparamvalue"]
        widgets = {
            "datafield": forms.TextInput(
                attrs={
                    "id": "txtbxdatafield",
                    "class": "form-control",
                    "placeholder": "Data Field",
                    "required": "required",
                }
            ),
            "datafor": forms.TextInput(
                attrs={
                    "id": "txtbxdatafor",
                    "class": "form-control",
                    "placeholder": "Data For",
                    "required": "required",
                }
            ),
            "dataparamtext": forms.TextInput(
                attrs={
                    "id": "txtbxparamtext",
                    "class": "form-control",
                    "placeholder": "Param Text",
                    "required": "required",
                }
            ),
            "dataparamvalue": forms.TextInput(
                attrs={
                    "id": "txtbxparamvalue",
                    "class": "form-control",
                    "placeholder": "Param Value",
                    "required": "required",
                }
            ),
        }

    def _validate_alphanumeric(self, fieldname, value):
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            FormError(
                message="Form Error: Validation:",
                original_exception=None,
                extra={
                    "Error": fieldname + " must contain only alphanumeric characters."
                },
            )
            raise forms.ValidationError("Value must be Alpha Numeric!!!")
        return value

    def clean_datafield(self):
        value = self.cleaned_data.get("datafield")
        value = self._validate_alphanumeric("Data Field", value)
        return value

    def clean_datafor(self):
        value = self.cleaned_data.get("datafor")
        value = self._validate_alphanumeric("Data For", value)
        return value

    def clean_dataparamtext(self):
        value = self.cleaned_data.get("dataparamtext")
        value = self._validate_alphanumeric("Param Text", value)
        return value

    def clean_dataparamvalue(self):
        value = self.cleaned_data.get("dataparamvalue")
        value = self._validate_alphanumeric("Param Value", value)
        return value
