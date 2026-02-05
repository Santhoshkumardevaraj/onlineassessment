from rest_framework import serializers

from apps.commonapp.models.AssessmentModels import Option


class OptionSerializer(serializers.ModelSerializer):
    option_signed_id = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ["id", "option_text", "option_signed_id"]

    def get_option_signed_id(self, obj):
        from django.core import signing

        return signing.dumps({"id": obj.id}, salt="assessmentconduct-salt")
