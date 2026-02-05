from django import forms
import re
from django.contrib.auth.models import User 
from apps.commonapp.models.UserModel import UserProfile
from apps.commonapp.exceptions.form_exceptions import FormError
from apps.assessment_admin.services.lookup_service import lookupservice

class UserProfileCreationForm(forms.Form):    
    first_name=forms.CharField(max_length=150,required=True,label="First Name",widget=forms.TextInput(attrs={'type':'text','id':'txtbxfirstname','name':'firstname','class':'form-control','placeholder':'First Name'}))
    last_name=forms.CharField(max_length=150,required=True,label="Last Name",widget=forms.TextInput(attrs={'type':'text','id':'txtbxlastname','name':'lastname','class':'form-control','placeholder':'Last Name'}))
    email=forms.EmailField(required=True,label="Email ID",widget=forms.TextInput(attrs={'type':'text','id':'txtbxemailid','name':'emailid','class':'form-control','placeholder':'Email ID'}))
    role=forms.ChoiceField(label="Role",choices=[],widget=forms.Select(attrs={'id':'ddlrole','name':'Role','class':'form-control'}),required=True)
    site=forms.ChoiceField(label="Site",choices=[],widget=forms.Select(attrs={'id':'ddlsite','name':'Site','class':'form-control'}),required=True)
    language=forms.ChoiceField(label="Language",choices=[],widget=forms.Select(attrs={'id':'ddllanguage','name':'Language','class':'form-control'}),required=True)

    def _validate_alpha(self, fieldname, value):
        if not re.match(r'^[a-zA-Z\s]+$', value):            
            FormError(message="Form Error: Validation:", original_exception=None,extra={"Error":fieldname+" must contain only alphabets."})
            raise forms.ValidationError("Value must be Alphabets")
        return value
    
    def clean_first_name(self):
        value = self.cleaned_data.get('first_name')
        value=self._validate_alpha("First Name", value)
        return value
    
    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')
        value=self._validate_alpha("Last Name", value)
        return value
    
    def __init__(self, *args, **kwargs):
        lookup_service=lookupservice()
        super().__init__(*args, **kwargs)
        field_map={'site':'site','language':'language','role':'userrole'}

        for field_name,field_key in field_map.items():
            if field_name in self.fields:
                lookups=lookup_service.get_filtered_lookup(datafield=field_key,datafor='all').order_by('dataparamvalue')

                self.fields[field_name].choices = [('', '--select--')] + [
                    (lookup.dataparamvalue, lookup.dataparamtext)
                    for lookup in lookups
                ]

#User Update Forms
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email'] 

        labels = {
            'username': 'username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email ID',
        }  
    username=forms.CharField(max_length=100,widget=forms.HiddenInput(attrs={'id':'hdfipusername','class':'form-control','name':'username'}))
    first_name=forms.CharField(max_length=100,label="First Name",widget=forms.TextInput(attrs={'id':'txtbxfirstname','class':'form-control','name':'first_name'}),required=True)
    last_name=forms.CharField(max_length=100,label="Last Name",widget=forms.TextInput(attrs={'id':'txtbxlastname','class':'form-control','name':'last_name'}),required=True)
    email=forms.CharField(max_length=100,label="Email",widget=forms.TextInput(attrs={'id':'txtbxemail','class':'form-control','name':'email'}),required=True)
    
    def _validate_alpha(self, fieldname, value):
        if not re.match(r'^[a-zA-Z\s]+$', value):            
            FormError(message="Form Error: Validation:", original_exception=None,extra={"Error":fieldname+" must contain only alphabets."})
            raise forms.ValidationError("Value must be Alphabets")
        return value
    
    def clean_first_name(self):
        value = self.cleaned_data.get('first_name')
        value=self._validate_alpha("First Name", value)
        return value
    
    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')
        value=self._validate_alpha("Last Name", value)
        return value    


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'site', 'language'] 

        labels = {
            'role': 'Role',
            'site': 'Site',
            'language': 'Language',
        }    
    role=forms.ChoiceField(label="Role",choices=[],widget=forms.Select(attrs={'id':'ddlrole','name':'Role','class':'form-control'}),required=True)
    site=forms.ChoiceField(label="Site",choices=[],widget=forms.Select(attrs={'id':'ddlsite','name':'Site','class':'form-control'}),required=True)
    language=forms.ChoiceField(label="Language",choices=[],widget=forms.Select(attrs={'id':'ddllanguage','name':'Language','class':'form-control'}),required=True)
    
    def __init__(self, *args, **kwargs):
        lookup_service=lookupservice()
        super().__init__(*args, **kwargs)
        field_map={'site':'site','language':'language','role':'userrole'}

        for field_name,field_key in field_map.items():
            if field_name in self.fields:
                lookups=lookup_service.get_filtered_lookup(datafield=field_key,datafor='all').order_by('dataparamvalue')

                self.fields[field_name].choices = [('', '--select--')] + [
                    (lookup.dataparamvalue, lookup.dataparamtext)
                    for lookup in lookups
                ]

      
class UserProfileListForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'site', 'language'] 

        labels = {
            'role': 'Role',
            'site': 'Site',
            'language': 'Language',
        }
    role=forms.ChoiceField(label="Role",choices=[],widget=forms.Select(attrs={'id':'ddlrole','name':'Role','class':'form-control'}),required=False)
    site=forms.ChoiceField(label="Site",choices=[],widget=forms.Select(attrs={'id':'ddlsite','name':'Site','class':'form-control'}),required=False)
    language=forms.ChoiceField(label="Language",choices=[],widget=forms.Select(attrs={'id':'ddllanguage','name':'Language','class':'form-control'}),required=False)

    def __init__(self, *args, **kwargs):
        lookup_service=lookupservice()
        super().__init__(*args, **kwargs)
        field_map={'site':'site','language':'language','role':'userrole'}

        for field_name,field_key in field_map.items():
            if field_name in self.fields:
                lookups=lookup_service.get_filtered_lookup(datafield=field_key,datafor='all').order_by('dataparamvalue')

                self.fields[field_name].choices = [('', '--select--')] + [
                    (lookup.dataparamvalue, lookup.dataparamtext)
                    for lookup in lookups
                ]

    

