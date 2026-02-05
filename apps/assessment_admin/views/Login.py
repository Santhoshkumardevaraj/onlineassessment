from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.assessment_admin.adminforms.login_credentials_form import (
    ChangePasswordForm, LoginForm)
from apps.assessment_admin.decorators import role_required
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.models import UserProfile
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


def adminhome(request):
    return HttpResponse("Admin Dashboard - Assessment Management")


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    objLoginForm = LoginForm()
    if request.method == "POST":
        objLoginForm = LoginForm(request.POST)
        if objLoginForm.is_valid():
            username = objLoginForm.cleaned_data["loginid"]
            password = objLoginForm.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    if user.is_superuser:
                        role = "Admin"
                    else:
                        role = user.userprofile.role

                    if role == "HR" or role == "Admin":
                        if password == "Change123":
                            return redirect("/onlineassessment/changepassword/")
                        else:
                            return redirect("/onlineassessment/assesspanel/")
                    elif role == "Candidate":
                        return redirect("/onlineassessment/candidatepanel/")
                    else:
                        messages.error(request, "Unknown role assigned.")
                except UserProfile.DoesNotExist:
                    messages.error(request, "User profile not found.")
            else:
                messages.error(request, "Invalid username or password")
        else:
            errordetails = {"formerror": objLoginForm.errors.as_json()}
            ViewError(
                message="login_view: Form Validation Failed:",
                original_exception=None,
                extra=errordetails,
                log=True,
            )
            messages.error(request, "Invalid or Incomplete data filled")
    return render(request, "login/login.html", {"LoginForm": objLoginForm})


@role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN])
def changepassword_view(request):
    objChangePasswordForm = ChangePasswordForm()
    if request.method == "POST":
        objChangePasswordForm = ChangePasswordForm(request.POST)
        if objChangePasswordForm.is_valid():
            newpassword = objChangePasswordForm.cleaned_data["newpassword"]
            confirmpassword = objChangePasswordForm.cleaned_data["confirmpassword"]
            CurrentUser = request.user
            user = get_object_or_404(User, username=CurrentUser)

            if user.userprofile.role != "Candidate":
                try:
                    user.set_password(str(newpassword))
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password Updated Successfully")
                    return redirect("/onlineassessment/assesspanel/")
                except Exception as Ex:
                    ViewError(
                        message="changepassword_view: Password change failed:",
                        original_exception=Ex,
                        extra=None,
                        log=True,
                    )
                    messages.error(request, "Error occured. Password change failed")
                    return redirect("/onlineassessment/changepassword/")
            else:
                return redirect("/onlineassessment/candidatepanel/")
        else:
            errordetails = {"formerror": objChangePasswordForm.errors.as_json()}
            ViewError(
                message="changepassword_view: Form Validation Failed:",
                original_exception=None,
                extra=errordetails,
                log=True,
            )
            messages.error(request, "Invalid or Incomplete data filled")

    return render(
        request,
        "login/changepassword.html",
        {"ChangePasswordForm": objChangePasswordForm},
    )


@role_required(["HR", "Admin"])
def dashboard(request):
    return render(request, "admin/Dashboard.html", {"pagetitle": "Dashboard"})
