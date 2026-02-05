"""
URL configuration for onlineassessment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from apps.assessment_admin.views.Login import login_view,logout_view,changepassword_view

app_name = "onlineassessment"

urlpatterns = [
    path("admin/", admin.site.urls),
     path("onlineassessment/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("", RedirectView.as_view(pattern_name="login", permanent=False)),
    path('', RedirectView.as_view(url='onlineassessment/login/', permanent=False)),    
    path('onlineassessment/login/', login_view, name='login'),
    path('onlineassessment/changepassword/', changepassword_view, name='changepassword'),   
    path('onlineassessment/logout/', logout_view, name='logout'),
    
    path('onlineassessment/assesspanel/', include('apps.assessment_admin.urls')),
    path('onlineassessment/candidatepanel/', include('apps.assessment_candidate.urls')),
    path('onlineassessment/onlineassessmentapi/', include('apps.assessment_api.urls')),
]
