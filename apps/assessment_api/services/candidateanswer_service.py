from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.candidateanswer_repository import CandidateAnswerRepository
from apps.commonapp.repositories.assessmentassign_repository import AssessmentConductRepository


class CandidateAnswerService:
    def __init__(self):
         self._candidateanswer_repo=CandidateAnswerRepository() 
    
    def read_candidate_questions(self,assessmentconductid):
        try:
            assessmentconduct_repo=AssessmentConductRepository()
            assessmentconduct=assessmentconduct_repo.get_assessmentconduct_by_id(recordid=assessmentconductid)
            candidate_answer_list=self._candidateanswer_repo.read_candidate_questions(assessmentconduct=assessmentconduct)
            return candidate_answer_list
        except Exception as Ex:
            raise ServiceError(message="CandidateAnswerService: Failed to get data: ",original_exception=Ex,extra=None,log=True)
    
    def candidate_questions_mark_read(self,recordid):
        try:
            
            assessmentconduct=self._candidateanswer_repo.candidate_questions_mark_read(recordid=recordid)
            
            return assessmentconduct
        except Exception as Ex:
            raise ServiceError(message="CandidateAnswerService: Failed to get data: ",original_exception=Ex,extra=None,log=True)
    
    def get_candidateanswer_by_id(self,recordid=None):
        try:
            
            assessmentconduct=self._candidateanswer_repo.get_candidateanswer_by_id(recordid=recordid)
            
            return assessmentconduct
        except Exception as Ex:
            raise ServiceError(message="CandidateAnswerService: Failed to get data: ",original_exception=Ex,extra=None,log=True)
        
        