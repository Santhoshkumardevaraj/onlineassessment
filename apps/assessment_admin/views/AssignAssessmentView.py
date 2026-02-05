from django.shortcuts import render, redirect
from django.core import signing

from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator


from django.views import View

from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.assessment_admin.adminforms.assessment_form import AssessmentCreateEditForm,AssessmentSearchForm

from apps.assessment_admin.services.assessment_service import AssessmentService
from apps.assessment_admin.services.assessmentassign_service import AssessmentAssignService
from apps.assessment_admin.services.useradministration_service import useradministrationservice


from apps.assessment_admin.decorators import role_required
from apps.commonapp.role_abbr_constants import ROLE_SUPER_ADMIN,ROLE_ADMIN

@method_decorator(role_required([ROLE_SUPER_ADMIN,ROLE_ADMIN]),name='dispatch')
class AssignAssessmentView(View):
    template_name='assessment/assignassessment.html'
    form_class = AssessmentCreateEditForm
    search_form=AssessmentSearchForm
    paginate_by=15    
    _assessmentservice=AssessmentService()
    _assessmentassignservice=AssessmentAssignService()
    _user_service=useradministrationservice()
    form_current_action=None
    form_card_class=None
    form_card_title=None
    assessment_report_list=None
    assigned_assessment=None

    def get_assessments_assigned_for_candidate(self,candidate_profile,currentuser):
        self.assigned_assessment=self._assessmentassignservice.check_assessmentconduct(candidate=candidate_profile,assessment=None,assessment_date=None,currentuser=currentuser)
        
        if self.assigned_assessment:
            #print(self.assigned_assessment.count())
            for item in self.assigned_assessment:
                item.signed_id=signing.dumps({'id':item.id},salt='assessmentconduct-salt')


    def get(self,request,*args,**kwargs):
        searched_username=None
        candidate_profile=None
        _searchform=None
        page_obj=None
        try:
            ActionName=request.GET.get('ActionName')
            cand_loginid=request.GET.get('username')
            if ActionName and ActionName=='removeassessmentconduct':
                selected_recordid=request.GET.get("assessmentconductidforaction")
                selected_recordid_decoded = signing.loads(selected_recordid, salt='assessmentconduct-salt', max_age=3600)
                if selected_recordid_decoded:
                    selected_recordid_decoded=selected_recordid_decoded['id']
                    assessment_conduct_toremove=self._assessmentassignservice.get_assessmentconduct_by_id(selected_recordid_decoded)
                    if assessment_conduct_toremove:
                        remove_assessmentconduct=self._assessmentassignservice.update_assessmentconduct_remove(assessment_conduct=assessment_conduct_toremove,currentuser=request.user)
                        if remove_assessmentconduct:
                            messages.success(request,"Assessment removed successfully")
                        else:
                            messages.error(request,"Assessment remove failed")
            if cand_loginid and cand_loginid!='':
                candidate_profile=self._user_service.get_user_list_filtered(loginid=cand_loginid,role="Candidate").first()
                
                if candidate_profile and candidate_profile.username:
                    self.get_assessments_assigned_for_candidate(candidate_profile,request.user)                    
                    searched_username=candidate_profile.username
                   
                    _searchform=self.search_form()
                    self.assessment_report_list=self._assessmentservice.read_recent_assessment()            
                
                    if self.assessment_report_list:
                        for assessment in self.assessment_report_list:
                            assessment.signed_id=signing.dumps({'id':assessment.id},salt='assessment-salt')
                        paginator = Paginator(self.assessment_report_list, self.paginate_by)
                        page_number = request.GET.get('page')
                        page_obj = paginator.get_page(page_number)
                else:
                    messages.error(request, "Candidate doesn't exist")


        except Exception as Ex:
            ViewError(message="AssignAssessmentView: Failed to get candidate data:", original_exception=Ex,log=True)
            messages.error(request, "An unexpected error occured")    
       
        context={
            'pagetitle':'Assign Assessment','AssessmentSearchForm':_searchform,'AssessmentList':self.assessment_report_list,'page_obj':page_obj,
                    'form_card_class':self.form_card_class,"form_card_title":self.form_card_title,"searched_username":searched_username,"candidate_profile":candidate_profile,
                    'assigned_assessment':self.assigned_assessment
                                    }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class()
        page_obj=None
        _searchform=self.search_form()
        ActionName=request.POST.get('ActionName')
        selected_recordid_decoded=0
        searched_username=None
        candidate_profile=None        


        try:
            cand_loginid=request.GET.get('username')
            if cand_loginid and cand_loginid!='':
                candidate_profile=self._user_service.get_user_list_filtered(loginid=cand_loginid).first()
                
                    
                    
        except Exception as Ex:
            ViewError(message="AssignAssessmentView: Failed to get candidate data:", original_exception=Ex,log=True)
            messages.error(request, "An unexpected error occured")
        
            
        if ActionName and ActionName=="assignassessment":
            try:
                selected_recordid=request.POST.get("assessmentidforaction")
                selected_assessmentdate=request.POST.get("assessmentdatetoassign")
                selected_recordid_decoded = signing.loads(selected_recordid, salt='assessment-salt', max_age=3600)
                if selected_recordid_decoded:
                    selected_recordid_decoded=selected_recordid_decoded['id']            
                    
                assessment=self._assessmentservice.get_assessment_by_id(recordid=selected_recordid_decoded)
                if selected_assessmentdate:
                    if assessment:
                        check_assessmentassigned=self._assessmentassignservice.check_assessmentconduct(candidate=candidate_profile,assessment=assessment,assessment_date=selected_assessmentdate,currentuser=request.user)
                        if check_assessmentassigned:
                            messages.warning(request, "Candidate already have another assessment pending")
                        else:
                            self._assessmentassignservice.create_assessmentconduct(candidate=candidate_profile,assessment=assessment,assessment_date=selected_assessmentdate,currentuser=request.user)                   
                            messages.success(request, "Assessment assigned successfully")
                    else:
                        messages.error(request, "Requested Data Not Found")
                else:
                    messages.error(request, "Assessment Date not filled")
            except Exception as Ex:
                ViewError(message="CreateAssessmentView: Failed to edit assessment:", original_exception=Ex,log=True)
                messages.error(request, "Page Error Please Escalate")          
        elif ActionName and ActionName=="updateassessment":
            form = self.form_class(request.POST)
            if form.is_valid():
                try:
                    updated_assessment_data=form.cleaned_data            
                    if updated_assessment_data:
                        assessment = self._assessmentservice.update_assessment(form.cleaned_data,currentuser=request.user)
                        if assessment:
                            form = self.form_class(instance=assessment)
                            self.form_current_action="UpdateAssessment"
                            messages.success(request, "Assessment Updated Successfully")
                            self.form_card_class="card-success"
                            self.form_card_title="Assessment Update"
                    else:   
                        messages.error(request, "Requested Data Nod Found")
                    #print(updated_assessment_data)
                except Exception as Ex:
                    ViewError(message="CreateAssessmentView: Failed to update assessment:", original_exception=Ex,extra=None,log=True)
                    messages.error(request, "Data Save Failed") 
            else:
                errordetails={'formerror':form.errors.as_json()}                 
                ViewError(message="CreateAssessmentView: Form Validation Failed:", original_exception=None,extra=errordetails,log=True)
                messages.error(request, "Invalid or Incomplete data filled")               
        elif ActionName and ActionName=="deleteassessment":
            selected_recordid=request.POST.get("assessmentidforaction")
            selected_recordid_decoded = signing.loads(selected_recordid, salt='assessment-salt', max_age=3600)
            if selected_recordid_decoded:
                selected_recordid_decoded=selected_recordid_decoded['id']
            
            try:
                delete_assessment=self._assessmentservice.get_assessment_by_id(recordid=selected_recordid_decoded)                 
                if delete_assessment:
                    assessment = self._assessmentservice.update_assessment_remove(delete_assessment,currentuser=request.user)
                    if assessment:
                        messages.success(request, "Assessment Deleted Successfully")
                else:   
                    messages.error(request, "Requested Data Nod Found")
                #print(updated_assessment_data)
            except Exception as Ex:
                ViewError(message="CreateAssessmentView: Failed to delete assessment:", original_exception=Ex,extra=None,log=True)
                messages.error(request, "Data Save Failed")    
            
        elif ActionName and ActionName=="saveassessment":
            form = self.form_class(request.POST)
            if form.is_valid():
                try:
                    assessment = self._assessmentservice.create_assessment(form.cleaned_data,currentuser=request.user)
                    if assessment:
                        messages.success(request, "Assessment Created Successfully")
                        return redirect('assessment-createedit')
                    else:
                        messages.error(request, "Data Save Failed")
                except Exception as Ex:
                    ViewError(message="CreateAssessmentView: Failed to save assessment:", original_exception=Ex,extra=None,log=True)
                    messages.error(request, "Data Save Failed")
            else:
                errordetails={'formerror':form.errors.as_json()}                 
                ViewError(message="CreateAssessmentView: Form Validation Failed:", original_exception=None,extra=errordetails,log=True)
                messages.error(request, "Invalid or Incomplete data filled")
        
        elif ActionName and ActionName=="searchassessment":
            form = self.search_form(request.POST)
            if form.is_valid():
                try:
                    self.assessment_report_list = self._assessmentservice.search_assessment(form.cleaned_data,currentuser=request.user)
                    if not self.assessment_report_list:
                        messages.error(request, "No Data Found")
                except Exception as Ex:
                    ViewError(message="CreateAssessmentView: Failed to search assessment:", original_exception=Ex,extra=None,log=True)
                    messages.error(request, "No Data Found")
            else:
                errordetails={'formerror':form.errors.as_json()}                 
                ViewError(message="CreateAssessmentView: Form Validation Failed:", original_exception=None,extra=errordetails,log=True)
                messages.error(request, "Invalid or Incomplete data filled")
        
        #Statement to check user and assigned assessment

        try:            
            if candidate_profile and candidate_profile.username:
                searched_username=candidate_profile.username
                self.get_assessments_assigned_for_candidate(candidate_profile,request.user)

                # On error, re-render the same page with form and list
                if not self.assessment_report_list:
                    self.assessment_report_list = self._assessmentservice.read_recent_assessment()
                if self.assessment_report_list:

                    for assessment in self.assessment_report_list:
                        assessment.signed_id=signing.dumps({'id':assessment.id},salt='assessment-salt')
                    paginator = Paginator(self.assessment_report_list, self.paginate_by)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    
                    
        except Exception as Ex:
            ViewError(message="AssignAssessmentView: Failed to get candidate data:", original_exception=Ex,log=True)
            messages.error(request, "An unexpected error occured")

        context = {
            'pagetitle': 'Create Assessment',
            'AssessmentForm': form,
            'searched_username':searched_username,
            'candidate_profile':candidate_profile,
            'assigned_assessment':self.assigned_assessment,
            'AssessmentSearchForm':_searchform,
            'ProfileList': self.assessment_report_list,
            'page_obj': page_obj,
            'form_current_action':self.form_current_action,
            'form_card_class':self.form_card_class,"form_card_title":self.form_card_title
        }
        return render(request, self.template_name, context)
