from django.db import transaction

from apps.commonapp.models.TypeLookupModel import TypeLookup
from apps.commonapp.exceptions.repository_exceptions import *

class TypeLookupRepository:  

    def __init__(self,model_class=TypeLookup):
        self.model=model_class    
    
    def create_typelookup(self,model_data:dict ,currentuser, **kwargs):
        try:            
            #typelookup_data={'datafield':datafield,'datafor':datafor,'dataparamtext':dataparamtext,'dataparamvalue':dataparamvalue}  
            typelookupobj=self.model(**model_data)
            typelookupobj.save(user=currentuser)          
            #self.model.objects.create(**model_data,user=currentuser)
            
        except Exception as Ex:
            raise RepositoryError(message="TypeLookup Repository: Failed to create lookup:", original_exception=Ex)       
    
    def update_typelookup_remove(self, typelookupid,currentuser=None):
        try:            
            with transaction.atomic():
                typelookup=self.model.objects.filter(id=typelookupid).first()
                typelookup.active = False
                typelookup.save(update_fields=["active","modified_by_id","modified_datetime"],user=currentuser)
                
            #self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.filter(id=typelookup.id)
        except Exception as Ex:
            raise RepositoryError(message="Typelookup Repository: Failed to remove lookup:", original_exception=Ex)
    
    def get_typelookup_filtered(self, datafield=None, datafor=None, dataparamtext=None, dataparamvalue=None):
        try:
            qs = self.model.objects.filter(active=True)
            if datafield:
                qs = qs.filter(datafield=datafield)
            if datafor:
                qs = qs.filter(datafor=datafor)
            if dataparamtext:
                qs = qs.filter(dataparamtext=dataparamtext)
            if dataparamvalue:
                qs = qs.filter(dataparamvalue=dataparamvalue)
            qs=qs.order_by('-created_datetime')
            return qs    
        except Exception as Ex:
            raise RepositoryError(message="Typelookup Repository: Failed to get lookup filtered:", original_exception=Ex)
    
     # datafield     datafor     dataparamtext     dataparamvalue 
    def get_all_lookup(self):
        try:
            return self.model.objects.filter(active=True).order_by('-created_datetime')
        except Exception as Ex:
            raise RepositoryError(message="Typelookup Repository: Failed to get all lookup:", original_exception=Ex)           
    
    

