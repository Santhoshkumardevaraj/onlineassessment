from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.views import View

from apps.assessment_admin.adminforms.typelookup_form import TypeLookupForm
from apps.commonapp.exceptions.view_exceptions import ViewError
from apps.assessment_admin.decorators import role_required
from apps.assessment_admin.services.lookup_service import lookupservice
from apps.commonapp.role_abbr_constants import ROLE_SUPER_ADMIN,ROLE_ADMIN

@method_decorator(role_required([ROLE_SUPER_ADMIN,ROLE_ADMIN]),name='dispatch')
class CreateEditLookupView(View):
    pagetitle='Lookup'
    template_name='admin/lookup.html'
    form_class=TypeLookupForm
    paginate_by=50
    _service=lookupservice()

    def get(self,request,*args,**kwargs):
        get_form=self.form_class()        
        try:
            sort_by = request.GET.get('sort', 'created_datetime')  # default sorting
            sort_order = request.GET.get('order', 'desc')  # 'asc' or 'desc'

            if sort_order == 'desc':
                sort_by = f"-{sort_by}"  # prefix with '-' for descending

            ListTypeLookup=self._service.get_all_lookup().order_by(sort_by)

            paginator=Paginator(ListTypeLookup,self.paginate_by)
            page_number=request.GET.get('page')
            page_obj=paginator.get_page(page_number)

        except Exception as Ex:
             ViewError(message="CreateEditLookupView: Failed in get method:", original_exception=Ex,extra=None,log=True)
             messages.error(request,"Error occured. please escalate")

        context={'pagetitle':self.pagetitle,'page_obj':page_obj,'TypeLookupForm':get_form,
                 "sort": request.GET.get("sort", "created_datetime"),"order": request.GET.get("order", "desc")}
        return render(request,self.template_name,context)
    
    def post(self,request,*args,**kwargs):        
        _currentuser=request.user
        actionname=request.POST.get("ActionName")
        deletelookupid=request.POST.get("deletelookupid")
        post_form=self.form_class()

        #print(post_form.is_valid())
        try:

            if request.POST.get("ActionName"):
                if actionname=="deletelookup" and deletelookupid:  
                    delete_lookup= self._service.remove_typelookup(lookup_id=deletelookupid,currentuser=_currentuser) 
                    if delete_lookup:
                        messages.success(request,"Data deleted successfully")
                    else:
                        messages.error(request,"Error occured please escalate")                     
                elif actionname=="createlookup":
                    post_form=self.form_class(request.POST)
                    if post_form.is_valid():
                        createlookup=self._service.create_lookup(post_form.cleaned_data,currentuser=_currentuser)
                        #ObjTypeLookupForm.save(user=request.user)
                        if createlookup:
                            messages.success(request, "Data Created Successfully.")
                            return redirect('admin-typelookupaddedit')
                        else:
                            messages.error(request,"Error occured in save please escalate")
                    else:
                        errordetails={'formerror':post_form.errors.as_json()}                 
                        ViewError(message="CreateEditLookupView: Form Validation Failed:", original_exception=None,extra=errordetails,log=True)
                        messages.error(request, "Invalid or Incomplete data filled")                          
        except Exception as Ex:
             ViewError(message="CreateEditLookupView: Failed to save data:", original_exception=Ex,extra=None,log=True)
             messages.error(request,"Error occured. please escalate")
            
        
        sort_by=request.GET.get('sort','created_datetime')
        sort_order=request.GET.get('order','desc')
        if sort_order=='desc':
            sort_by=f"-{sort_by}"
        ListTypeLookup=self._service.get_all_lookup().order_by(sort_by)
        paginator=Paginator(ListTypeLookup,self.paginate_by)
        page_number=request.GET.get('page',1)
        page_obj=paginator.get_page(page_number)

        context={'pagetitle':self.pagetitle,'page_obj':page_obj,'TypeLookupForm':post_form,
                 "sort": request.GET.get("sort", "created_datetime"),"order": request.GET.get("order", "desc")}
        return render(request,self.template_name,context)

