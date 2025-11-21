from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from app.exceptions import AnswerAlreadyAccepted
from answers.models import Answer


class AnswerModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['content', 'question']

    def validate(self, attrs):
        question = attrs.get('question')
        if question and question.is_solutioned:
            raise AnswerAlreadyAccepted()

        return attrs


class AnswerDetailModelSerializer(serializers.ModelSerializer):
    quantity_upvotes = serializers.SerializerMethodField()
    profile_name1 = serializers.CharField(source='author.user.first_name')
    profile_name2 = serializers.CharField(source='author.user.last_name')

    class Meta:
        model = Answer
        fields = ['profile_name1', 'profile_name2', 'content', 'is_accepted',
                  'created_at', 'question', 'quantity_upvotes']

    @extend_schema_field(serializers.IntegerField())
    def get_quantity_upvotes(self, obj):
        return obj.upvotes.count()


class AnswerUpdateModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['content']


class AnswerSolutionedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['is_accepted']

    def validate(self, attrs):
        if attrs.get('is_accepted'):
            question = self.instance.question

            already_accepted = Answer.objects.filter(
                question=question,
                is_accepted=True
            ).exclude(pk=self.instance.pk).exists()

            if already_accepted:
                raise AnswerAlreadyAccepted

        return attrs
