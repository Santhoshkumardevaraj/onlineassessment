from django.contrib.auth.decorators import login_required
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def flatten_roles(roles):
    for r in roles:
        if isinstance(r, list):
            yield from flatten_roles(r)
        else:
            yield r

def role_required(expected_role):

    allowed = set(flatten_roles(expected_role))
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'userprofile'):
                user_role=request.user.userprofile.role
                #print(user_role,allowed)
                if user_role in allowed:
                    return view_func(request,*args,**kwargs)
                else:
                    messages.warning(request,"Unauthorized Access")
                    if user_role=="Candidate":
                        return redirect('login')
                    else:
                        return redirect('admin-dashboard')
            else:
                messages.warning(request,"User Not Found")
                return redirect('login')
            #return redirect('login')    
            #return HttpResponseForbidden("Access Denied: Unauthorized Role")
        return _wrapped_view
    return decorator