from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth.models import User, Group
from profiles.models import UserProfile
from credentials.serializers import CredentialDetailDeleteModelSerializer


class UserModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']
    
class UserProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'avatar', 'expertise']

    def create(self, validated_data):
        user = validated_data.pop('user')
        password = user.pop('password')
        new_user = User.objects.create_user(password=password, **user)

        customer_profile = Group.objects.get(name='Customer profile')
        new_user.groups.add(customer_profile)

        new_profile = UserProfile.objects.create(user=new_user, **validated_data)

        return new_profile

class UserProfileUpdateModelSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserProfile
        fields = ['pk', 'first_name', 'last_name', 'bio', 'avatar', 'expertise']
        extra_kwargs = {'pk': {'read_only': True}}

class UserProfileDetailModelSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    credentials = CredentialDetailDeleteModelSerializer(many=True, read_only=True)
    articles_written = serializers.SerializerMethodField()
    answers_accepted = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['pk', 'first_name', 'last_name', 'bio', 'avatar', 'expertise', 'reputation_score', 'articles_written', 'answers_accepted', 'is_professional', 'credentials']
        extra_kwargs = {'pk': {'read_only': True}}

    @extend_schema_field(serializers.IntegerField())
    def get_articles_written(self, obj):
        return obj.article_author.count()    

    @extend_schema_field(serializers.IntegerField())
    def get_answers_accepted(self, obj):
        return obj.answer_author.filter(is_accepted=True).count()

class UserProfileDeleteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'
