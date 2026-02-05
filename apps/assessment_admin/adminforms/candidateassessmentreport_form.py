from django import forms
import re
import regex
from apps.commonapp.models import Assessment,Question,Option
from apps.commonapp.exceptions.form_exceptions import FormError
from apps.assessment_admin.services.lookup_service import lookupservice

class CandidateAssessmentReportForm(forms.Form):
    assessment_fromdate =forms.DateField(label="Assessment From Date",widget=forms.DateInput(attrs={'type':'date','id':'txtbxassessmentfromdate','class':'form-control','placeholder':'From Date'}),required=True)
    assessment_tillate =forms.DateField(label="Assessment Till Date",widget=forms.DateInput(attrs={'type':'date','id':'txtbxassessmenttilldate','class':'form-control','placeholder':'From Date'}),required=True)
    title=forms.CharField(label="Title",widget=forms.TextInput(attrs={'type':'text','id':'txtbxtitle','class':'form-control','placeholder':'Title'}),max_length=200,required=False)
    assessmentlanguage=forms.ChoiceField(label="Language",choices=[],widget=forms.Select(attrs={'id':'ddlassessmentlanguage','name':'Language','class':'form-control'}),required=False)

    candidatesite=forms.ChoiceField(label="Site",choices=[],widget=forms.Select(attrs={'id':'ddlcandidatesite','name':'Language','class':'form-control'}),required=False)
    candidatelanguage=forms.ChoiceField(label="Language",choices=[],widget=forms.Select(attrs={'id':'ddlcandidatelanguage','name':'Language','class':'form-control'}),required=False)
    candidatefirstname=forms.CharField(label="firstname",widget=forms.TextInput(attrs={'id':'txtbxfirstname','name':'firstname','class':'form-control','placeholder':'First Name'}),required=False)
    candidatelastname=forms.CharField(label="lastname",widget=forms.TextInput(attrs={'id':'txtbxlastname','name':'lastname','class':'form-control','placeholder':'Last Name'}),required=False)    
    candidateemailid=forms.EmailField(label="Email ID",widget=forms.TextInput(attrs={'type':'text','id':'txtbxemailid','name':'emailid','class':'form-control','placeholder':'Email ID'}),required=False)


   
    def _validate_alphanumeric(self, fieldname, value):
        # Allowed letters for French, English, Spanish, Italian, Portuguese + numbers + basic punctuation
        ALLOWED_PATTERN = r'^[A-Za-z0-9ÀÁÂÃÄÅàáâãäåÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÇçÑñŸÿ\s,.\-!?\'_¿¡]+$'
        if not re.fullmatch(ALLOWED_PATTERN, value):            
            FormError(message="Form Error: Validation:", original_exception=None,extra={"Error":fieldname+" must contain only alphanumeric characters."})
            raise forms.ValidationError("Invalid characters fpund: only letters, numbers, spaces and basic punctuation are allowed")
        return value
    
    def _validate_numeric(self, fieldname, value):
        if not re.match(r'^[0-9\s]+$', value):            
            FormError(message="Form Error: Validation:", original_exception=None,extra={"Error":fieldname+" must contain only numeric characters."})
            raise forms.ValidationError("Value must be Numeric")
        return value

    def clean_title(self):
        value = self.cleaned_data.get('title')
        if value:
            value=self._validate_alphanumeric("Title", value)
        return value
    
    def clean_description(self):
        value = self.cleaned_data.get('description')
        if not value.strip():
            raise forms.ValidationError("Description Cannot be Empty")
        return value

    def clean_num_of_questions(self):
        value = self.cleaned_data.get('num_of_questions')
        if value<1 or value>100:
            raise forms.ValidationError("Value must be 1 to 100")
        return value

    def clean_duration_minutes(self):
        value = self.cleaned_data.get('duration_minutes')
        if value<1 or value>100:
            raise forms.ValidationError("Value must be 1 to 100")
        return value
    
    def __init__(self, *args, **kwargs):
        lookup_service=lookupservice()
        super().__init__(*args, **kwargs)
        field_map={'assessmentlanguage':'language','candidatelanguage':'language','candidatesite':'site'}

        for field_name,field_key in field_map.items():
            if field_name in self.fields:
                lookups=lookup_service.get_filtered_lookup(datafield=field_key,datafor='all').order_by('dataparamvalue')

                self.fields[field_name].choices = [('', '--select--')] + [
                    (lookup.dataparamvalue, lookup.dataparamtext)
                    for lookup in lookups
                ]
