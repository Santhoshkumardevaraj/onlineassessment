import random

from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.user_repository import UserRepository


class useradministrationservice:

    def __init__(self):
        self.user_repo = UserRepository()

    def get_user_list_filtered(self, site=None, role=None, language=None, loginid=None):
        try:
            return self.user_repo.get_users_filtered(
                site=site, role=role, language=language, loginid=loginid
            )
        except Exception as Ex:
            ServiceError(
                message="CreateUserView: Failed to get data:",
                original_exception=Ex,
                log=True,
            )

    def get_user_recent50(self):
        try:
            return self.user_repo.get_recent_users(limit=50)
        except Exception as Ex:
            ServiceError(
                message="CreateUserView: Failed to get data:",
                original_exception=Ex,
                log=True,
            )
        # return CustomUser.objects.read_recent50_profile()
