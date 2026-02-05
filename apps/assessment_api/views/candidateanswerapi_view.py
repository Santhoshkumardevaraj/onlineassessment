from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import signing
import json
from datetime import datetime,timedelta

from apps.assessment_api.services.candidateanswer_service import CandidateAnswerService
from apps.assessment_candidate.services.assessmentassign_service import AssessmentAssignService
from apps.assessment_api.services.assessment_service import AssessmentService
from apps.assessment_api.serializers.option_serializer import OptionSerializer

from apps.assessment_api.serializers.CandidateAnswerUpdate_serializer import CandidateAnswerUpdateSerializer
from apps.commonapp.exceptions.view_exceptions import ViewError

class DefaultView(APIView):
    def get(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})
    
class CandidateAnswerView(APIView):
    _candidateanswer_service=CandidateAnswerService()

    def __init__(self):
        self._assessment_assign_service=AssessmentAssignService()

    def update_assessemnt_start_time(self,selected_assessmentconductid_decoded):
        assigned_assessment=self._assessment_assign_service.get_assessmentconduct_by_id(recordid=selected_assessmentconductid_decoded)
        if not assigned_assessment.assessment_start_datetime:
            self._assessment_assign_service.update_assessmentconduct_starttime(selected_assessmentconductid_decoded)
    
    def get_time_remaining_inseconds(self, selected_assessmentconductid_decoded):
        assigned_assessment=self._assessment_assign_service.get_assessmentconduct_by_id(recordid=selected_assessmentconductid_decoded)
        if assigned_assessment and assigned_assessment.assessment_start_datetime:
            allowed_duration_minutes=assigned_assessment.assessment.duration_minutes
            current_datetime=datetime.now()
            assessment_starttime=assigned_assessment.assessment_start_datetime

            assessment_starttime=assessment_starttime.strftime('%Y-%m-%d %H:%M:%S')
            current_datetime=current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            assessment_starttime=datetime.strptime(assessment_starttime,'%Y-%m-%d %H:%M:%S')
            current_datetime=datetime.strptime(current_datetime,'%Y-%m-%d %H:%M:%S')

            end_assessment_time=assessment_starttime+timedelta(minutes=allowed_duration_minutes)
            
            time_remaining=(end_assessment_time-current_datetime).total_seconds()

            return time_remaining
            

    def get(self,request,*args,**kwargs):
        assessmentconductid=request.GET.get('assessmentconductid')

        selected_assessmentconductid_decoded=0
        selected_assessmentconductid=assessmentconductid       
        selected_assessmentconductid_decoded = signing.loads(selected_assessmentconductid, salt='assessmentconduct-salt', max_age=28800)
        if selected_assessmentconductid_decoded:
            selected_assessmentconductid_decoded=selected_assessmentconductid_decoded['id']

            candidateanswer_list=self._candidateanswer_service.read_candidate_questions(assessmentconductid=selected_assessmentconductid_decoded)
            if not candidateanswer_list:
                return Response(
                    {"result":"No Records Found"},
                    status=status.HTTP_204_NO_CONTENT
                )
            
            self.update_assessemnt_start_time(selected_assessmentconductid_decoded)
            time_remaining_inseconds=self.get_time_remaining_inseconds(selected_assessmentconductid_decoded)
            data = [{'signed_id': signing.dumps({'id': candidate_answer.question.id}, salt='assessmentconduct-salt'),'question_status':candidate_answer.question_status}for candidate_answer in candidateanswer_list
                    ]
            #Update assessment start time
            

            return Response({"result":data,'time_remaining_inseconds':time_remaining_inseconds},status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "An unexpected error occured"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})

class CandidateAnswer_questionView(APIView):
    _candidateanswer_service=CandidateAnswerService()
    _assessment_service=AssessmentService()
    def get(self,request,*args,**kwargs):
        assessmentconductid=request.GET.get('assessmentconductid')
        currentquestionid=request.GET.get('currentquestionid')
        candidateanswer_list=None
        candidate_answer_id=None
        current_question_id=None
        previous_question_id=None
        next_question_id=None
        current_question=None
        current_options=None
        candidate_option_id=None

        if assessmentconductid:
            selected_assessmentconductid_decoded=0
            selected_assessmentconductid=assessmentconductid       
            selected_assessmentconductid_decoded = signing.loads(selected_assessmentconductid, salt='assessmentconduct-salt', max_age=28800)
            if selected_assessmentconductid_decoded:
                selected_assessmentconductid_decoded=selected_assessmentconductid_decoded['id']
                candidateanswer_list=self._candidateanswer_service.read_candidate_questions(assessmentconductid=selected_assessmentconductid_decoded)

        if currentquestionid:
            selected_currentquestionid_decoded=0
            selected_currentquestionid=currentquestionid       
            selected_currentquestionid_decoded = signing.loads(selected_currentquestionid, salt='assessmentconduct-salt', max_age=28800)
            if selected_currentquestionid_decoded:
                selected_currentquestionid_decoded=selected_currentquestionid_decoded['id']
                current_question_readed=self._assessment_service.get_question_by_id(selected_currentquestionid_decoded)
                if current_question_readed:
                    current_question=current_question_readed.text
                    current_question_id=signing.dumps({'id': current_question_readed.id}, salt='assessmentconduct-salt')
                    current_options=current_question_readed.options.filter(active=True)

                    

                    if candidateanswer_list:
                        candidateanswer_list = list(candidateanswer_list)
                        ids = [ca.question.id for ca in candidateanswer_list]

                        if selected_currentquestionid_decoded in ids:
                            idx = ids.index(selected_currentquestionid_decoded)

                            # Previous question (if any)
                            if idx > 0:
                                previous_id = ids[idx - 1]
                                previous_question_id = signing.dumps({'id': previous_id}, salt='assessmentconduct-salt')
                            else:
                                previous_question_id = None

                            # Next question (if any)
                            if idx < len(ids) - 1:
                                next_id = ids[idx + 1]
                                next_question_id = signing.dumps({'id': next_id}, salt='assessmentconduct-salt')
                            else:
                                next_question_id = None
                            
                            options = current_question_readed.options.filter(active=True)
                            serializer = OptionSerializer(options, many=True)
                            current_options = serializer.data

                            current_candidate_answer_id=candidateanswer_list[idx].id
                            res=self._candidateanswer_service.candidate_questions_mark_read(recordid=current_candidate_answer_id)
                            candidate_answer_id=signing.dumps(current_candidate_answer_id, salt='assessmentconduct-salt') 
                            candidate_option_id=res.selected_option_id




        
        if not candidateanswer_list:
            return Response(
                {"result":"No Records Found"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        

        
        #print(candidateanswer_list)
        data = [
    {        
        'current_question_id': current_question_id,
        'previous_question_id': previous_question_id,
        'next_question_id': next_question_id,
        'current_question': current_question,
        'current_options': current_options,
        'candidate_answer_id':candidate_answer_id,
        'candidate_option_id':candidate_option_id
        
    }    
]

        return Response({"result":data},status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})

class CandidateAnswer_OptionView(APIView):

    _candidateanswer_service=CandidateAnswerService()
    _assessment_service=AssessmentService()
    _candidateansweroption_serializer=CandidateAnswerUpdateSerializer()
    def get(self,request,*args,**kwargs):
        assessmentconductid=request.GET.get('assessmentconductid')
        questionid=request.GET.get('currentquestionid')
        candidateanswerid=request.GET.get('candidateanswerid')
        candidateoptionid=request.GET.get('optionid')
       
        try:
            if candidateanswerid:
                selected_candidateanswerid_decoded=0
                selected_candidateanswerid=candidateanswerid       
                selected_candidateanswerid_decoded = signing.loads(selected_candidateanswerid, salt='assessmentconduct-salt', max_age=28800)

                selected_candidateansweroptionid_decoded=0
                selected_candidateansweroptionid=candidateoptionid       
                selected_candidateansweroptionid_decoded = selected_candidateansweroptionid #signing.loads(selected_candidateansweroptionid, salt='assessmentconduct-salt', max_age=28800)

                #if selected_candidateansweroptionid_decoded:
                    #selected_candidateansweroptionid_decoded=selected_candidateansweroptionid_decoded['id']
                if selected_candidateanswerid_decoded:                    
                    candidateanswer=self._candidateanswer_service.get_candidateanswer_by_id(recordid=selected_candidateanswerid_decoded)

                    serializer = CandidateAnswerUpdateSerializer(candidateanswer, data={"option_id": selected_candidateansweroptionid_decoded}, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        except Exception as Ex:
            ViewError(message="APIView Error: Failed to get data: ",original_exception=Ex,extra=None,log=True)
            return Response({"error": "An unexpected error occured"}, status=status.HTTP_404_NOT_FOUND)
        

        #print(candidateanswer_list)
        data = [
    {        
        "success": True,
        
    }    
]

        return Response({"result":data},status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})

class CandidateEndAssessmentView(APIView):
    _candidateanswer_service=CandidateAnswerService()

    def __init__(self):
        self._assessment_assign_service=AssessmentAssignService()

    def update_assessemnt_end(self,selected_assessmentconductid_decoded,assessment_endtype):
        assigned_assessment=self._assessment_assign_service.get_assessmentconduct_by_id(recordid=selected_assessmentconductid_decoded)
        if assigned_assessment.assessment_start_datetime and not assigned_assessment.assessment_end_datetime:
            self._assessment_assign_service.update_assessmentconduct_end(recordid=selected_assessmentconductid_decoded,type_of_closure=assessment_endtype)
                
   
    def get(self,request,*args,**kwargs):
        assessmentconductid=request.GET.get('assessmentconductid')
        assessment_endtype=request.GET.get('endtype')


        selected_assessmentconductid_decoded=0
        selected_assessmentconductid=assessmentconductid       
        selected_assessmentconductid_decoded = signing.loads(selected_assessmentconductid, salt='assessmentconduct-salt', max_age=28800)
        if selected_assessmentconductid_decoded:
            selected_assessmentconductid_decoded=selected_assessmentconductid_decoded['id']
           
            self.update_assessemnt_end(selected_assessmentconductid_decoded,assessment_endtype)            
            #Update assessment start time

            return Response({"result":"success"},status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "An unexpected error occured"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self,request,*args,**kwargs):
        return Response({'result':"stringtest"})