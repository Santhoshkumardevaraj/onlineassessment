from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.assessment_repository import \
    AssessmentRepository


class AssessmentService:
    def __init__(self):
        self._assessment_repo = AssessmentRepository()

    def read_recent_assessment(self):
        try:
            assessment_list = self._assessment_repo.get_recent_assessment()
            return assessment_list
        except Exception as Ex:
            raise ServiceError(
                message="CreateAssessmentview: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def search_assessment(self, cleaned_data, currentuser):
        try:
            assessment_list = self._assessment_repo.get_assessment_filtered(
                assessment_data=cleaned_data, currentuser=currentuser
            )
            return assessment_list
        except Exception as Ex:
            raise ServiceError(
                message="CreateAssessmentview: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def get_assessment_by_id(self, recordid):
        try:
            assessment_list = self._assessment_repo.get_assessment_by_id(
                recordid=recordid
            )
            return assessment_list
        except Exception as Ex:
            raise ServiceError(
                message="CreateAssessmentview: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def read_question_by_assessment(self, assessment=None):
        try:
            question_list = self._assessment_repo.read_question_by_assessment(
                assessment=assessment
            )
            return question_list
        except Exception as Ex:
            raise ServiceError(
                message="CreateQuestionService: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def search_question_bytext(self, assessment=None, srchtext=None):
        try:
            question_list = self._assessment_repo.search_question_bytext(
                assessment=assessment, srchtext=srchtext
            )
            return question_list
        except Exception as Ex:
            raise ServiceError(
                message="CreateQuestionService: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def get_question_by_id(self, recordid):
        try:
            ind_question = self._assessment_repo.get_question_by_id(recordid=recordid)
            return ind_question
        except Exception as Ex:
            raise ServiceError(
                message="CreateAssessmentview: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )
