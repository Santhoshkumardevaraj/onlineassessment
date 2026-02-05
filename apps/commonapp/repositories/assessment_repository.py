from django.db import transaction

from apps.commonapp.models.AssessmentModels import Assessment,Question,Option
from apps.commonapp.exceptions.repository_exceptions import *

class AssessmentRepository:

    def __init__(self,model_class=Assessment):
        self.model=model_class    
    
    def create_assessment(self,model_data:dict,currentuser):
        try:
            objassessmentdetails=self.model(**model_data)
            objassessmentdetails.save(user=currentuser)
            
            return objassessmentdetails
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to create assessment:", original_exception=Ex)       
    
    def update_assessment(self, assessment_data=None,currentuser=None):
        try:
            assessment_edit=Assessment.objects.get(id=assessment_data['id']) 
            with transaction.atomic():                
                for attr,value in assessment_data.items():
                    if attr!='id':
                        setattr(assessment_edit,attr,value)
                assessment_edit.save(user=currentuser)                
            #self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=assessment_data['id'])
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to update assessment:", original_exception=Ex)
        
    def update_assessment_remove(self, assessment_data=None,currentuser=None):
        try:
            #print(type(assessment_data))
            assessment_edit=Assessment.objects.get(id=assessment_data.id) 
            with transaction.atomic():                
                assessment_edit.deactivate(user=currentuser)

                for question in assessment_edit.questions.all():
                    question.deactivate(user=currentuser)

                    for option in question.options.all():
                        option.deactivate(user=currentuser)
                  
            #self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=assessment_data.id)
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to remove assessment:", original_exception=Ex)
    
    def get_assessment_filtered(self, assessment_data=None,currentuser=None):
        try:
            qs = Assessment.objects.filter(active=True)
            if assessment_data['srchtitle']:
                qs = qs.filter(title__icontains=assessment_data['srchtitle'])
            if assessment_data['srchlanguage']:
                qs = qs.filter(language=assessment_data['srchlanguage'])           
            if assessment_data['srchnum_of_questions']:
                qs = qs.filter(num_of_questions=assessment_data['srchnum_of_questions'])
            
            qs=qs.order_by('-created_datetime')
            return qs    
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to get assessments filtered:", original_exception=Ex)
    
    
    def get_recent_assessment(self,limit=50):
        try:
            return self.model.objects.filter(active=True).order_by('-created_datetime')[:limit]
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to get recent Assessment:", original_exception=Ex)
    
    def get_assessment_by_id(self,recordid):
        try:
            return self.model.objects.filter(id=recordid).first()
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to get assessment by recordid:", original_exception=Ex)

    def create_question(self,assessment=None,Question_model_data=None,List_model_options=None,currentuser=None):
        try:
            if not assessment or not Question_model_data:
                raise ValueError("Both assessment and questions are needed")
            
            curr_assessment=self.model.objects.get(id=assessment.id)

            question=Question.objects.create(assessment=curr_assessment,text=Question_model_data['text'],question_type=Question_model_data['question_type'],created_by=currentuser)
            if List_model_options:
                for opt_data in List_model_options:
                    if opt_data.get('option') and opt_data.get('option')!='':
                        Option.objects.create(
                            question=question,
                            option_text=opt_data.get('option'),
                            is_correct=opt_data.get('is_correct', False),
                            created_by=currentuser
                        )           
            
            return curr_assessment
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to create questions and options:", original_exception=Ex)       

    def update_question_and_options(self,cleaned_data, question, currentuser):
        try:
            with transaction.atomic():
                # Update question fields
                question.text = cleaned_data['question_text']
                question.question_type = cleaned_data['question_type']
                question.modified_by = currentuser
                question.save(update_fields=['text', 'question_type', 'modified_by', 'modified_datetime'])

                # Clear old options (or update existing)
                existing_options = list(question.options.all())
                correct_index = int(cleaned_data['correct_option'])

                # Loop through possible option inputs
                for i in range(4):
                    opt_text = cleaned_data.get(f'option_{i+1}')
                    if not opt_text:
                        # If option was previously saved but now blank → deactivate or delete
                        if i < len(existing_options):
                            existing_options[i].delete()
                        continue

                    is_correct = (i == correct_index)

                    # If option exists, update; else create new
                    if i < len(existing_options):
                        opt = existing_options[i]
                        opt.option_text = opt_text
                        opt.is_correct = is_correct
                        opt.modified_by = currentuser
                        opt.save(update_fields=['option_text', 'is_correct', 'modified_by', 'modified_datetime'])
                    else:
                        Option.objects.create(
                            question=question,
                            option_text=opt_text,
                            is_correct=is_correct,
                            created_by=currentuser
                        )
                return question
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to update questions and options:", original_exception=Ex)

    def read_question_by_assessment(self,assessment=None):
        try:
            if not assessment:
                raise ValueError("Both assessment and questions are needed")
            
            curr_assessment=self.model.objects.get(id=assessment.id)

            List_Questions=Question.objects.filter(active=True,assessment=curr_assessment.id).order_by('-created_datetime')
           
            return List_Questions
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to read question by assessment:", original_exception=Ex)      

    def search_question_bytext(self,assessment=None,srchtext=None):
        try:
            if not assessment:
                raise ValueError("Both assessment and questions are needed")
            
            curr_assessment=self.model.objects.get(id=assessment.id)

            List_Questions=Question.objects.filter(active=True,assessment=curr_assessment.id,text__icontains=srchtext).order_by('-created_datetime')
           
            return List_Questions
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to read question by hint:", original_exception=Ex) 
    
    def get_question_by_id(self,recordid):
        try:
            return Question.objects.filter(id=recordid).first()
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to read question by recordid:", original_exception=Ex)

    def update_question_remove(self, question_data=None,currentuser=None):
        try:
            #print(type(assessment_data))
            question_edit=Question.objects.get(id=question_data.id)
            options_edit=Option.objects.filter(question=question_edit) 
            with transaction.atomic():                
                question_edit.deactivate(user=currentuser)

                for option in options_edit:
                    option.deactivate(user=currentuser)               
            #self.model.objects.filter(id=user_id).update(**update_data)
            return "success"
        except Exception as Ex:
            raise RepositoryError(message="Assessment Repository: Failed to remove question and option:", original_exception=Ex)
        return None
