from datetime import datetime, timedelta

from apps.commonapp.exceptions.service_exceptions import ServiceError
from apps.commonapp.repositories.assessmentassign_repository import \
    AssessmentConductRepository


class AssessmentAssignService:
    def __init__(self):
        self._assessmentconduct_repo = AssessmentConductRepository()

    def create_assessmentconduct(
        self, candidate=None, assessment=None, assessment_date=None, currentuser=None
    ):
        try:

            assessmentconduct = (
                self._assessmentconduct_repo.create_assessmentconductcreate(
                    candidate=candidate,
                    assessment=assessment,
                    assessment_date=assessment_date,
                    currentuser=currentuser,
                )
            )

            return assessmentconduct
        except Exception as Ex:
            raise ServiceError(
                message="AssessmentAssignService: Failed to create assessment conduct",
                original_exception=Ex,
                log=True,
            )

    def check_assessmentconduct(
        self, candidate=None, assessment=None, assessment_date=None, currentuser=None
    ):
        try:

            assessmentconduct = self._assessmentconduct_repo.check_assessmentconduct(
                candidate=candidate,
                assessment=assessment,
                assessment_date=assessment_date,
                currentuser=currentuser,
            )

            if assessmentconduct:
                for assessmentcond in assessmentconduct:
                    if assessmentcond.assessment_start_datetime:
                        assessment_duration = assessmentcond.assessment.duration_minutes
                        assessment_Start_time = assessmentcond.assessment_start_datetime
                        assessment_Start_time_expected_end = (
                            assessment_Start_time
                            + timedelta(minutes=assessment_duration)
                        )
                        current_datetime = datetime.now()
                        assessment_Start_time_expected_end = datetime.strptime(
                            assessment_Start_time_expected_end.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        current_datetime = datetime.strptime(
                            current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        print(assessment_Start_time_expected_end, current_datetime)
                        if current_datetime < assessment_Start_time_expected_end:
                            assessmentcond.type_of_closure = None
                        else:
                            self._assessmentconduct_repo.auto_close_assignedassessment(
                                assessmentconduct=assessmentcond
                            )
                            assessmentcond.type_of_closure = "auto_close"
                    else:
                        assessmentcond.type_of_closure = None

            return assessmentconduct.filter(type_of_closure=None)
        except Exception as Ex:
            raise ServiceError(
                message="AssessmentAssignService: Failed to create assessment conduct",
                original_exception=Ex,
                log=True,
            )

    def update_assessment(self, cleaned_data, currentuser):
        try:
            model_data = cleaned_data
            assessment = self._assessmentconduct_repo.update_assessment(
                assessment_data=model_data, currentuser=currentuser
            )
            return assessment
        except Exception as Ex:
            raise ServiceError(
                message="CreateUserView: Failed to get data:",
                original_exception=Ex,
                log=True,
            )

    def update_assessmentconduct_remove(
        self, assessment_conduct=None, currentuser=None
    ):
        try:
            model_data = assessment_conduct
            assessmentconduct_remove = (
                self._assessmentconduct_repo.update_assessmentconduct_remove(
                    model_data=model_data, currentuser=currentuser
                )
            )
            return assessmentconduct_remove
        except Exception as Ex:
            raise ServiceError(
                message="AssessmentAssignService: Failed to remove data:",
                original_exception=Ex,
                log=True,
            )

    def read_recent_assessment(self):
        try:
            assessment_list = self._assessmentconduct_repo.get_recent_assessment()
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
            assessment_list = self._assessmentconduct_repo.get_assessment_filtered(
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

    def get_assessmentconduct_by_id(self, recordid):
        try:
            assessmentconduct_list = (
                self._assessmentconduct_repo.get_assessmentconduct_by_id(
                    recordid=recordid
                )
            )
            return assessmentconduct_list
        except Exception as Ex:
            raise ServiceError(
                message="AssessmentAssignService: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )

    def get_assessmentconduct_by_filter(
        self,
        assessment_fromdate=None,
        assessment_lastdate=None,
        assessment_assessmenttitle=None,
        assessment_assessmentlanguage=None,
        candidate_site=None,
        candidate_language=None,
        candidate_firstname=None,
        candidate_lastname=None,
        candidate_mailid=None,
    ):
        try:
            assessmentconduct_list = (
                self._assessmentconduct_repo.get_assessmentconduct_by_filter(
                    assessment_fromdate=assessment_fromdate,
                    assessment_lastdate=assessment_lastdate,
                    assessment_assessmenttitle=assessment_assessmenttitle,
                    assessment_assessmentlanguage=assessment_assessmentlanguage,
                    candidate_site=candidate_site,
                    candidate_language=candidate_language,
                    candidate_firstname=candidate_firstname,
                    candidate_lastname=candidate_lastname,
                    candidate_mailid=candidate_mailid,
                )
            )
            return assessmentconduct_list
        except Exception as Ex:
            raise ServiceError(
                message="AssessmentAssignService: Failed to get data: ",
                original_exception=Ex,
                extra=None,
                log=True,
            )
