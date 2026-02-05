import random

from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.user_repository import UserRepository

class useradministrationservice:

    def __init__(self):
        self.user_repo=UserRepository()

    def create_user_and_profile(self,cleaned_data,currentuser):
        try:
            role = cleaned_data.get('role')
            email = cleaned_data.get('email')
            first_name = cleaned_data.get('first_name')
            last_name = cleaned_data.get('last_name')
            site=cleaned_data.get('site')
            language=cleaned_data.get('language')

            # Business logic
            if role == 'Candidate':
                last_user = self.user_repo.get_last_candidate_username(loginprefix='CAND')
                number = int(last_user.username.replace('CAND',''))+1 if last_user else 100
                username = f'CAND{number}'
                password = random.randint(100000,999999)
                candpassword=str(password)
            else:
                username = email
                password = 'Change123'
                candpassword=None          

            password=str(password)
            # Repository handles DB
            user = self.user_repo.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name, is_staff=(role != 'Candidate'),role=role,site=site,language=language, candpassword=candpassword,currentuser=currentuser)

            return user
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)

    def update_user_and_profile(self,user, user_data, profile_data,currentuser):
        successflag=True
        try:

            self.user_repo.update_user_and_profile(
            user=user,
            user_data=user_data,
            profile_data=profile_data,
            currentuser=currentuser
        )
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)
            successflag=False
        return successflag
    
    def update_user_and_profile_password(self,user, default_password, candpassword,currentuser):
        successflag=True
        try:

            self.user_repo.update_user_and_profile_password(
            user=user,
            default_password=default_password,
            candpassword=candpassword,
            currentuser=currentuser
            )
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)
            successflag=False
        return successflag
    
    def update_user_and_profile_delete(self,user,currentuser):
        successflag=True
        try:
            self.user_repo.update_user_and_profile_delete(
            user=user,
            currentuser=currentuser
            )
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)
            successflag=False
        return successflag

    def get_user_list_filtered(self,site=None,role=None, language=None,loginid=None):
        try:
            return self.user_repo.get_users_filtered(site=site,role=role, language=language,loginid=loginid)
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)

    def get_user_recent50(self):
        try:
            return self.user_repo.get_recent_users(limit=50)
        except Exception as Ex:
            ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)
        #return CustomUser.objects.read_recent50_profile()