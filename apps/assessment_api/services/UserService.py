from apps.assessment_api.models import CustomUser
from apps.commonapp.Utility import UtilityMaster as UTM

def get_UserListFiltered(site=None,role=None,language=None,loginid=None,loginidmatch=None):
    return CustomUser.objects.filter_users(site=site,role=role,language=language,loginid=loginid,loginidmatch=loginidmatch)
