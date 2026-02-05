from datetime import date, datetime, timedelta

from django.db import transaction
from django.utils import timezone

from apps.commonapp.exceptions.repository_exceptions import *
from apps.commonapp.models.AssessmentConductModels import AssessmentConduct


class AssessmentConductRepository:
    # assessment, candidate, assessment_date, assessment_start_datetime, assessment_end_datetime, type_of_closure, duration, score, remarks
    def __init__(self, model_class=AssessmentConduct):
        self.model = model_class

    def create_assessmentconductcreate(
        self, candidate=None, assessment=None, assessment_date=None, currentuser=None
    ):
        try:
            objassessmentconductdetails = self.model(
                assessment=assessment,
                candidate=candidate,
                assessment_date=assessment_date,
            )
            objassessmentconductdetails.save(user=currentuser)

            return objassessmentconductdetails
        except Exception as Ex:
            raise RepositoryError(
                message="AssessmentConductRepository: Failed to create assessment conduct:",
                original_exception=Ex,
            )

    def update_assessment(self, assessment_data=None, currentuser=None):
        try:
            assessment_edit = AssessmentConduct.objects.get(id=assessment_data["id"])
            with transaction.atomic():
                for attr, value in assessment_data.items():
                    if attr != "id":
                        setattr(assessment_edit, attr, value)
                assessment_edit.save(user=currentuser)
            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=assessment_data["id"])
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to update assessment:",
                original_exception=Ex,
            )

    def update_assessmentconduct_remove(self, model_data=None, currentuser=None):
        try:
            # print(type(assessment_data))
            assessment_edit = AssessmentConduct.objects.get(id=model_data.id)
            with transaction.atomic():
                assessment_edit.deactivate(user=currentuser)

            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=model_data.id)
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to remove assessment:",
                original_exception=Ex,
            )

    def check_assessmentconduct(
        self, candidate=None, assessment=None, assessment_date=None, currentuser=None
    ):
        try:

            yesterday_Date = date.today() - timedelta(days=1)

            assessmentdateframe_min = datetime.strptime(
                yesterday_Date.strftime("%Y-%m-%d"), "%Y-%m-%d"
            ).date()
            assessmentdateframe_max = datetime.strptime(
                date.today().strftime("%Y-%m-%d"), "%Y-%m-%d"
            ).date()

            qs = AssessmentConduct.objects.filter(
                active=True,
                assessment_end_datetime=None,
                type_of_closure=None,
                assessment_date__gte=assessmentdateframe_min,
                assessment_date__lte=assessmentdateframe_max,
            )
            if candidate:
                qs = qs.filter(candidate=candidate)
            if assessment:
                # qs = qs.filter(assessment=assessment)
                pass
            if assessment_date:
                # qs = qs.filter(assessment_date=assessment_date)
                pass

            qs = qs.order_by("-created_datetime")
            return qs
        except Exception as Ex:
            raise RepositoryError(
                message="AssessmentConductRepository: Failed to get assessments filtered:",
                original_exception=Ex,
            )

    def auto_close_assignedassessment(self, assessmentconduct=None):
        try:
            # print(type(assessment_data))
            aassessmentconduct_edit = AssessmentConduct.objects.get(
                id=assessmentconduct.id
            )
            with transaction.atomic():
                aassessmentconduct_edit.assessment_end_datetime = datetime.now()
                aassessmentconduct_edit.type_of_closure = "auto_closed"
                aassessmentconduct_edit.save()

            # self.model.objects.filter(id=user_id).update(**update_data)
            return True
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to remove assessment:",
                original_exception=Ex,
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
            qs = AssessmentConduct.objects.filter(active=True)
            # assessment,candidate,assessment_date,assessment_start_datetime,assessment_end_datetime,type_of_closure,duration,score,remarks
            if assessment_fromdate:
                qs = qs.filter(assessment_date__gte=assessment_fromdate)
            if assessment_lastdate:
                qs = qs.filter(assessment_date__lte=assessment_lastdate)

            qs = qs.order_by("-created_datetime")
            return qs
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to get assessments filtered:",
                original_exception=Ex,
            )

    def get_assessment_filtered(self, assessment_data=None, currentuser=None):
        try:
            qs = AssessmentConduct.objects.filter(active=True)
            if assessment_data["srchtitle"]:
                qs = qs.filter(title__icontains=assessment_data["srchtitle"])
            if assessment_data["srchlanguage"]:
                qs = qs.filter(language=assessment_data["srchlanguage"])
            if assessment_data["srchnum_of_questions"]:
                qs = qs.filter(num_of_questions=assessment_data["srchnum_of_questions"])

            qs = qs.order_by("-created_datetime")
            return qs
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to get assessments filtered:",
                original_exception=Ex,
            )

    def get_recent_assessment(self, limit=50):
        try:
            return self.model.objects.filter(active=True).order_by("-created_datetime")[
                :limit
            ]
        except Exception as Ex:
            raise RepositoryError(
                message="Assessment Repository: Failed to get recent Assessment:",
                original_exception=Ex,
            )

    def get_assessmentconduct_by_id(self, recordid):
        try:
            return self.model.objects.filter(id=recordid).first()
        except Exception as Ex:
            raise RepositoryError(
                message="AssessmentConductRepository: Failed to get assessment conduct by recordid:",
                original_exception=Ex,
            )

    def update_assessementconduct_start_time(self, recordid=None):
        try:
            assessmentconduct_edit = AssessmentConduct.objects.get(id=recordid)
            with transaction.atomic():
                assessmentconduct_edit.assessment_start_datetime = datetime.now()
                assessmentconduct_edit.save()
            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=recordid)
        except Exception as Ex:
            raise RepositoryError(
                message="AssessmentConductRepository Repository: Failed to update assessment:",
                original_exception=Ex,
            )

    def update_assessmentconduct_end(self, recordid=None, type_of_closure=None):
        try:
            assessmentconduct_edit = AssessmentConduct.objects.get(id=recordid)

            with transaction.atomic():
                assessmentconduct_edit.assessment_end_datetime = datetime.now()
                assessmentconduct_edit.type_of_closure = type_of_closure
                assessmentconduct_edit.save()
            # self.model.objects.filter(id=user_id).update(**update_data)
            return self.model.objects.get(id=recordid)
        except Exception as Ex:
            raise RepositoryError(
                message="AssessmentConductRepository Repository: Failed to update assessment:",
                original_exception=Ex,
            )
