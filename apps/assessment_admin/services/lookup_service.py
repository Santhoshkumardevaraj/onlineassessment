from apps.commonapp.models import TypeLookup

from apps.commonapp.repositories.typelookup_repository import TypeLookupRepository
from apps.commonapp.exceptions.service_exceptions import ServiceError

class lookupservice:

    def __init__(self):
        self.current_repo=TypeLookupRepository()

    def create_lookup(self,cleaned_data,currentuser):    
        successflag=True
        try:
            datafield=cleaned_data.get('datafield')
            datafor=cleaned_data.get('datafor')
            dataparamtext=cleaned_data.get('dataparamtext')
            dataparamvalue=cleaned_data.get('dataparamvalue')
            #print(currentuser)
            model_data={'datafield':datafield,'datafor':datafor,'dataparamtext':dataparamtext,'dataparamvalue':dataparamvalue}  
            self.current_repo.create_typelookup(model_data,currentuser) 
        except Exception as Ex:
            ServiceError(message="Service_typeLookup: Failed to get data:", original_exception=Ex,log=True)
            successflag=False 
        return successflag

    def remove_typelookup(self,lookup_id,currentuser):
        successflag=True
        try:
            self.current_repo.update_typelookup_remove(lookup_id,currentuser)
            successflag=True
        except Exception as Ex:
            ServiceError(message="Service_typeLookup: Failed to get data:", original_exception=Ex,log=True)
            successflag=False
        return successflag

    def get_all_lookup(self):
        try:
            return self.current_repo.get_all_lookup().order_by('-created_datetime')
            #return TypeLookup.objects.filter_typelookup().order_by('-created_datetime')
        except Exception as Ex:
            ServiceError(message="Service_typeLookup: Failed to get data:", original_exception=Ex,log=True)
    
    def get_filtered_lookup(self,datafield=None,datafor=None,dataparamtext=None,dataparamvalue=None):
        try:
            return self.current_repo.get_typelookup_filtered(datafield=datafield,datafor=datafor,dataparamtext=dataparamtext,dataparamvalue=dataparamvalue).order_by('-created_datetime')
        except Exception as Ex:
            ServiceError(message="Service_typeLookup: Failed to get data:", original_exception=Ex,log=True)