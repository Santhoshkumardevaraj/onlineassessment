from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json

from apps.assessment_api.services import UserService

class DefaultView(APIView):
    def get(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})
    
class UserProfileView(APIView):
    def get(self,request,*args,**kwargs):
        loginidmatch=request.GET.get('loginidmatch')

        user_data=UserService.get_UserListFiltered(loginidmatch=loginidmatch)
        if not user_data:
            return Response(
                {"result":"No Records Found"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        data=list(user_data.values('username')) if hasattr(user_data,"values") else list(user_data)        

        return Response({"result":data},status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})

class CandidateProfileView(APIView):
    def get(self,request,*args,**kwargs):
        loginidmatch=request.GET.get('loginidmatch')

        user_data=UserService.get_UserListFiltered(loginidmatch=loginidmatch,role='Candidate')
        if not user_data:
            return Response(
                {"result":"No Records Found"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        data=list(user_data.values('username')) if hasattr(user_data,"values") else list(user_data)        

        return Response({"result":data},status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})