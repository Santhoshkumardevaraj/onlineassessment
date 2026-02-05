from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.assessment_repository import AssessmentRepository

class AssessmentService:
    def __init__(self):
         self._assessment_repo=AssessmentRepository() 
    def create_assessment(self,cleaned_data,currentuser):
        try:
            title = cleaned_data.get('title')
            description = cleaned_data.get('description')
            language = cleaned_data.get('language')
            num_of_questions = cleaned_data.get('num_of_questions')
            duration_minutes=cleaned_data.get('duration_minutes')

            model_data={'title':title,'description':description,'language':language,'num_of_questions':num_of_questions,'duration_minutes':duration_minutes}

            assessment = self._assessment_repo.create_assessment(model_data=model_data,currentuser=currentuser)

            return assessment
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)

    def update_assessment(self,cleaned_data,currentuser):
        try:
            model_data=cleaned_data
            assessment = self._assessment_repo.update_assessment(assessment_data=model_data,currentuser=currentuser)
            return assessment
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)    
    
    def update_assessment_remove(self,cleaned_data,currentuser):
        try:
            model_data=cleaned_data
            assessment = self._assessment_repo.update_assessment_remove(assessment_data=model_data,currentuser=currentuser)
            return assessment
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)    

    def read_recent_assessment(self):
        try:
            assessment_list=self._assessment_repo.get_recent_assessment()
            return assessment_list
        except Exception as Ex:
            raise ServiceError(message="CreateAssessmentview: Failed to get data: ",original_exception=Ex,extra=None,log=True)
    
    def search_assessment(self,cleaned_data,currentuser):
        try:
            assessment_list=self._assessment_repo.get_assessment_filtered(assessment_data=cleaned_data,currentuser=currentuser)
            return assessment_list
        except Exception as Ex:
            raise ServiceError(message="CreateAssessmentview: Failed to get data: ",original_exception=Ex,extra=None,log=True)
    
    def get_assessment_by_id(self,recordid):
        try:
            assessment_list=self._assessment_repo.get_assessment_by_id(recordid=recordid)
            return assessment_list
        except Exception as Ex:
            raise ServiceError(message="CreateAssessmentview: Failed to get data: ",original_exception=Ex,extra=None,log=True)
    
    ### QUESTION FUNCTIONS ###
    def create_question(self,curr_assessment=None,cleaned_data=None,currentuser=None):
        try:
            assessment = curr_assessment
            text = cleaned_data.get('question_text')
            question_type = cleaned_data.get('question_type')

            option_1 = cleaned_data.get('option_1')
            option_2 = cleaned_data.get('option_2')
            option_3 = cleaned_data.get('option_3')
            option_4 = cleaned_data.get('option_4')
            correct_option=cleaned_data.get('correct_option')
            if correct_option:
                correct_option=int(correct_option)
            List_options=[]
            List_model_options=[]
            List_options.append(option_1)
            List_options.append(option_2)
            List_options.append(option_3)
            List_options.append(option_4)
            for loopcount in range(0,len(List_options)):
                option_model_data={'option':List_options[loopcount],'is_correct':loopcount==correct_option}
                List_model_options.append(option_model_data)


            Question_model_data={'text':text,'question_type':question_type}

            assessment = self._assessment_repo.create_question(assessment=curr_assessment,Question_model_data=Question_model_data,List_model_options=List_model_options,currentuser=currentuser)

            return assessment
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)
    
    def read_question_by_assessment(self,assessment=None):
        try:            
            question_list=self._assessment_repo.read_question_by_assessment(assessment=assessment)
            return question_list
        except Exception as Ex:
            raise ServiceError(message="CreateQuestionService: Failed to get data: ",original_exception=Ex,extra=None,log=True)

    def search_question_bytext(self,assessment=None,srchtext=None):
        try:            
            question_list=self._assessment_repo.search_question_bytext(assessment=assessment,srchtext=srchtext)
            return question_list
        except Exception as Ex:
            raise ServiceError(message="CreateQuestionService: Failed to get data: ",original_exception=Ex,extra=None,log=True)

    def get_question_by_id(self,recordid):
        try:
            ind_question=self._assessment_repo.get_question_by_id(recordid=recordid)
            return ind_question
        except Exception as Ex:
            raise ServiceError(message="CreateAssessmentview: Failed to get data: ",original_exception=Ex,extra=None,log=True)    

    def update_question_remove(self,cleaned_data,currentuser):
        try:
            model_data=cleaned_data
            assessment = self._assessment_repo.update_question_remove(question_data=model_data,currentuser=currentuser)
            return assessment
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)

    def update_question_and_options(self,cleaned_data,question,currentuser):
        try:
            model_data=cleaned_data
            question = self._assessment_repo.update_question_and_options(cleaned_data,question,currentuser)
            return question
        except Exception as Ex:
            raise ServiceError(message="CreateUserView: Failed to get data:", original_exception=Ex,log=True)       
    