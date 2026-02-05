import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q


class LoginForm(forms.Form):
    loginid = forms.CharField(
        label="Login ID",
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "id": "txtbxloginid",
                "name": "loginid",
                "class": "form-control",
                "placeholder": "Login ID",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "id": "txtbxpassword",
                "name": "password",
                "class": "form-control",
                "placeholder": "password",
            }
        ),
    )


class ChangePasswordForm(forms.Form):
    newpassword = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "id": "txtbxnewpassword",
                "name": "newpassword",
                "class": "form-control",
                "placeholder": "new password",
            }
        ),
        min_length=8,
        max_length=15,
        required=True,
    )
    confirmpassword = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "id": "txtbxconfirmpassword",
                "name": "confimrpassword",
                "class": "form-control",
                "placeholder": "confirm password",
            }
        ),
        min_length=8,
        max_length=15,
        required=True,
    )

    def clean_newpassword(self):
        password = self.cleaned_data.get("newpassword")
        if not re.match(r"^[a-zA-Z0-9]+$", password):
            raise ValidationError("Password must contain only alphanumeric characters")
        return password

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("newpassword")
        confirm_pwd = cleaned_data.get("confirmpassword")

        if pwd and confirm_pwd and pwd != confirm_pwd:
            raise ValidationError("Passwords doesnt match!!!")
