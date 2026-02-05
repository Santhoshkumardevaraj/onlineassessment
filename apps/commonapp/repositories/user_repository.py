from django.contrib.auth.models import User
from django.db import transaction

from apps.commonapp.exceptions.repository_exceptions import *
from apps.commonapp.models import UserProfile


class UserRepository:

    def __init__(self, user_model=User):
        self.model = user_model

    def create_user(
        self,
        username,
        email,
        password,
        role,
        site,
        language,
        candpassword,
        currentuser,
        **kwargs
    ):
        try:
            user = self.model.objects.create_user(
                username=username, email=email, password=password, **kwargs
            )
            user_profile_data = {
                "user": user,
                "role": role,
                "site": site,
                "language": language,
                "candpassword": candpassword,
            }

            user_profile = UserProfile.objects.create(**user_profile_data)
            if hasattr(user_profile, "created_by"):
                user_profile.created_by = currentuser
                user_profile.save(update_fields=["created_by"])
            return user
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to Create User:", original_exception=Ex
            )

    def update_user_and_profile(
        self, user, user_data=None, profile_data=None, currentuser=None
    ):
        try:
            user_data = user_data or {}
            profile_data = profile_data or {}

            with transaction.atomic():
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()

                profile, _created = (
                    UserProfile.objects.select_for_update().get_or_create(user=user)
                )
                # print(profile,profile_data)
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save(user=currentuser)
            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.filter(id=user.id)
        except Exception as Ex:
            raise RepositoryError(
                message="UserRepository: Failed to Update user data:",
                original_exception=Ex,
            )

    def update_user_and_profile_password(
        self, user, default_password=None, candpassword=None, currentuser=None
    ):
        try:
            with transaction.atomic():
                user.set_password(str(default_password))
                user.save(update_fields=["password"])
                user.userprofile.save(
                    update_fields=["modified_by_id", "modified_datetime"],
                    user=currentuser,
                )
                # print(currentuser)

                if candpassword is not None:
                    user.userprofile.candpassword = str(candpassword)
                    user.userprofile.save(
                        update_fields=[
                            "candpassword",
                            "modified_by_id",
                            "modified_datetime",
                        ],
                        user=currentuser,
                    )

            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.filter(id=user.id)
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to reset password:",
                original_exception=Ex,
            )

    def update_user_and_profile_delete(self, user, currentuser=None):
        try:
            with transaction.atomic():
                user.is_active = False
                user.save(update_fields=["is_active"])

                user.userprofile.active = 0
                user.userprofile.save(
                    update_fields=["active", "modified_by_id", "modified_datetime"],
                    user=currentuser,
                )

            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.filter(id=user.id)
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to remove user:", original_exception=Ex
            )

    def get_users_filtered(self, site=None, role=None, language=None, loginid=None):
        try:
            qs = User.objects.filter(is_active=True)
            if site:
                qs = qs.filter(userprofile__site=site)
            if role:
                roles = role if isinstance(role, list) else [role]
                qs = qs.filter(userprofile__role__in=roles)
            if language:
                qs = qs.filter(userprofile__language=language)
            if loginid:
                qs = qs.filter(username=loginid)
            qs = qs.order_by("-userprofile__created_datetime")
            return qs
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to filter user data:",
                original_exception=Ex,
            )

    def get_recent_users(self, limit=50):
        try:
            return (
                self.model.objects.filter(is_active=True)
                .select_related("userprofile")
                .order_by("-userprofile__created_datetime")[:limit]
            )
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to get recent users:",
                original_exception=Ex,
            )

    def get_by_username(self, username):
        try:
            return self.model.objects.filter(username=username).first()
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to get by username:",
                original_exception=Ex,
            )

    def get_last_candidate_username(self, loginprefix):
        try:
            return (
                self.model.objects.filter(username__startswith=loginprefix)
                .order_by("-username")
                .first()
            )
        except Exception as Ex:
            raise RepositoryError(
                message="User Repository: Failed to get data last candidate username:",
                original_exception=Ex,
            )
