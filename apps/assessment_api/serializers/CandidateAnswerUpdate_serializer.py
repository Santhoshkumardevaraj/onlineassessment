from rest_framework import serializers
from apps.commonapp.models import CandidateAnswer, Option

class CandidateAnswerUpdateSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CandidateAnswer
        fields = ['id', 'option_id']

    def update(self, instance, validated_data):
        option_id = validated_data.get('option_id')
        try:
            selected_option = Option.objects.get(id=option_id)
        except Option.DoesNotExist:
            raise serializers.ValidationError("Invalid option selected.")

        # Update the candidate answer
        instance.selected_option = selected_option
        instance.question_status = 'answered'
        instance.is_correct = selected_option.is_correct
        instance.score = 1.0 if selected_option.is_correct else 0.0

        instance.save()
        return instance