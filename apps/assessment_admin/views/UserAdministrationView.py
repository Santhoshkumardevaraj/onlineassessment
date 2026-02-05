import random

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from apps.assessment_admin.adminforms.userprofile_form import (
    UserProfileCreationForm, UserProfileListForm, UserProfileUpdateForm,
    UserUpdateForm)
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.useradministration_service import \
    useradministrationservice
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.commonapp.role_abbr_constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class CreateUserView(View):
    template_name = "admin/createuser.html"
    form_class = UserProfileCreationForm
    _service = useradministrationservice()
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        _userform, profile_list, page_obj = [None] * 3

        try:
            _userform = self.form_class()
            profile_list = self._service.get_user_recent50()
            if profile_list:
                paginator = Paginator(profile_list, self.paginate_by)
                page_number = request.GET.get("page", 1)
                page_obj = paginator.get_page(page_number)
        except Exception as Ex:
            ViewError(
                message="CreateUserView: Error on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "Create User",
            "UserCreateForm": _userform,
            "ProfileList": profile_list,
            "page_obj": page_obj,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        profile_list, page_obj = [None] * 2
        form = self.form_class(request.POST)
        _currentuser = request.user
        if form.is_valid():
            try:
                user_profile = self._service.create_user_and_profile(
                    form.cleaned_data, _currentuser
                )
                if user_profile:
                    messages.success(request, "Data Created Successfully")
                    return redirect("admin-createuser")
                else:
                    messages.error(request, "Data Save Failed")
            except Exception as Ex:
                ViewError(
                    message="CreateUserView: Error on save/create user:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Data Save Failed")
        else:
            errordetails = {"formerror": form.errors.as_json()}
            ViewError(
                message="CreateUserView: Form Validation Failed:",
                original_exception=None,
                extra=errordetails,
                log=True,
            )
            messages.error(request, "Invalid or Incomplete data filled")

        # On error, re-render the same page with form and list
        profile_list = self._service.get_user_recent50()
        if profile_list:
            paginator = Paginator(profile_list, self.paginate_by)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

        context = {
            "pagetitle": "Create User",
            "UserCreateForm": form,
            "ProfileList": profile_list,
            "page_obj": page_obj,
        }
        return render(request, self.template_name, context)


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class UpdateUserView(View):
    template_name = "admin/updateuser.html"
    _service = useradministrationservice()
    _userupdateform = UserUpdateForm
    _userprofileupdateform = UserProfileUpdateForm

    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        user_form = profile_form = None
        user = user_profile = None

        if username:
            try:
                # user = get_object_or_404(User, username=username)

                user_qs = self._service.get_user_list_filtered(loginid=username)
                user = user_qs.first() if user_qs else None
                user_form = None
                profile_form = None
                if user:
                    user_profile = getattr(user, "userprofile", None)
                    if request.user.userprofile.role == "Admin":
                        user_form = self._userupdateform(instance=user)
                        profile_form = self._userprofileupdateform(
                            instance=user_profile
                        )
                    else:
                        if user_profile.role in ["Candidate"]:
                            user_form = self._userupdateform(instance=user)
                            profile_form = self._userprofileupdateform(
                                instance=user_profile
                            )
                        else:
                            messages.warning(request, "Unauthorized to edit this user")

                if not user:
                    messages.warning(request, "User not Found!!!")

            except Exception as Ex:
                ViewError(
                    message="UpdateUserView: Error on get method:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Data Save Failed")

        context = {
            "pagetitle": "Update User",
            "user_form": user_form,
            "profile_form": profile_form,
            "searched_username": username,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.GET.get("username")
        # user = get_object_or_404(User, username=username)
        user_qs = self._service.get_user_list_filtered(loginid=username)
        user = user_qs.first() if user_qs else None
        user_profile = user.userprofile
        _currentuser = request.user

        if not user:
            messages.warning(request, "User not Found!!!")

        user_form = self._userupdateform(request.POST, instance=user)
        profile_form = self._userprofileupdateform(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                formaction = request.POST.get("actionname")
                if formaction and formaction == "save":
                    update_success = self._service.update_user_and_profile(
                        user,
                        user_form.cleaned_data,
                        profile_form.cleaned_data,
                        currentuser=_currentuser,
                    )
                    if update_success:
                        messages.success(request, "Data Updated Successfully")
                    else:
                        messages.error(request, "Data Update Failed. Please escalate.")

                if formaction and formaction == "resetpassword":
                    default_password = "Change123"
                    candpassword = None
                    if user.userprofile.role == "Candidate":
                        default_password = random.randint(100000, 999999)
                        candpassword = str(default_password)
                    update_success = self._service.update_user_and_profile_password(
                        user, default_password, candpassword, currentuser=_currentuser
                    )
                    if update_success:
                        messages.success(request, "Data Updated Successfully")
                    else:
                        messages.error(request, "Data Update Failed. Please escalate.")

                if formaction and formaction == "deleteaccount":
                    user.is_active = False
                    user_profile.active = 0
                    update_success = self._service.update_user_and_profile_delete(
                        user, currentuser=_currentuser
                    )
                    if update_success:
                        messages.success(request, "Data Updated Successfully")
                        user_form = None
                        profile_form = None
                    else:
                        messages.error(request, "Data Update Failed. Please escalate.")

                if formaction and formaction == "cancelform":
                    user_form = None
                    profile_form = None

            except Exception as Ex:
                ViewError(
                    message="UpdateUserView: Error update user details:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Page Error Please Escalate")
        else:
            errordetails = {
                "user_form_errors": user_form.errors.as_json(),
                "profile_form_errors": profile_form.errors.as_json(),
                "username": request.GET.get("username"),
                "submitted_data": request.POST.dict(),
            }
            ViewError(
                message="UpdateUserView: Form Validation Failed:",
                original_exception=None,
                extra=errordetails,
                log=True,
            )
            messages.error(request, "Invalid or Incomplete data filled")

        context = {
            "pagetitle": "Update User",
            "user_form": user_form,
            "profile_form": profile_form,
            "searched_username": username,
        }
        return render(request, self.template_name, context)


@method_decorator(role_required([ROLE_SUPER_ADMIN, ROLE_ADMIN]), name="dispatch")
class ListUserView(View):
    template_name = "admin/listuser.html"
    form_class = UserProfileListForm
    paginate_by = 15
    _service = useradministrationservice()

    def get(self, request, *args, **kwargs):
        get_form = self.form_class()
        page_obj = None
        try:
            profile_list = self._service.get_user_recent50()
            paginator = Paginator(profile_list, self.paginate_by)
            page_number = request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)
        except Exception as Ex:
            ViewError(
                message="ListUserView: Error on get method:",
                original_exception=Ex,
                log=True,
            )
            messages.error(request, "Page Error Please Escalate")

        context = {
            "pagetitle": "List User",
            "page_obj": page_obj,
            "UserListForm": get_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post_form = self.form_class(request.POST)
        ProfileList = []
        if post_form.is_valid():
            try:
                sitefilter = post_form.cleaned_data.get("site")
                languagefilter = post_form.cleaned_data.get("language")
                rolefilter = post_form.cleaned_data.get("role")

                ProfileList = self._service.get_user_list_filtered(
                    site=sitefilter, role=rolefilter, language=languagefilter
                )
            except Exception as Ex:
                ViewError(
                    message="ListUserView: Failed on post method:",
                    original_exception=Ex,
                    log=True,
                )
                messages.error(request, "Page Error Please Escalate")
        else:
            errordetails = {"formerror": post_form.errors.as_json()}
            ViewError(
                message="ListUserView: Form Validation Failed:",
                original_exception=None,
                extra=errordetails,
                log=True,
            )
            messages.error(request, "Invalid or Incomplete data filled")

        paginator = Paginator(ProfileList, self.paginate_by)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context = {
            "pagetitle": "List User",
            "page_obj": page_obj,
            "UserListForm": post_form,
        }
        return render(request, self.template_name, context)
