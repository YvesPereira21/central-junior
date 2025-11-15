from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from questions.models import Question
from technologies.models import Technology
from technologies.serializers import TechnologyDetailSerializer
from answers.serializers import AnswerDetailModelSerializer


class QuestionModelSerializer(serializers.ModelSerializer):
    technologies = serializers.PrimaryKeyRelatedField(
        queryset=Technology.objects.all(),
        many=True
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'technologies']

class QuestionListModelSerializer(serializers.ModelSerializer):
    technologies = TechnologyDetailSerializer(many=True, read_only=True)
    quantity_likes = serializers.SerializerMethodField()
    profile_name1 = serializers.CharField(source='profile.user.first_name')
    profile_name2 = serializers.CharField(source='profile.user.last_name')

    class Meta:
        model = Question
        fields = ['pk', 'title', 'content', 'is_solutioned', 'created_at',
                  'technologies', 'profile_name1', 'profile_name2', 'quantity_likes']

    @extend_schema_field(serializers.IntegerField())
    def get_quantity_likes(self, obj):
        return obj.likes.count()

class QuestionDetailModelSerializer(serializers.ModelSerializer):
    technologies = TechnologyDetailSerializer(many=True, read_only=True)
    answers = AnswerDetailModelSerializer(many=True, read_only=True)
    quantity_likes = serializers.SerializerMethodField()
    profile_name1 = serializers.CharField(source='profile.user.first_name')
    profile_name2 = serializers.CharField(source='profile.user.last_name')

    class Meta:
        model = Question
        fields = ['title', 'content', 'is_solutioned', 'created_at', 
                  'technologies', 'profile_name1', 'profile_name2', 'quantity_likes']

    @extend_schema_field(serializers.IntegerField())
    def get_quantity_likes(self, obj):
        return obj.likes.count()

class QuestionDeleteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['is_published']

class QuestionSolutionedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['is_solutioned']
