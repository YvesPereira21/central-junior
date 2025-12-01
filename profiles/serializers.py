from rest_framework import serializers
from django.contrib.auth.models import User, Group
from profiles.models import UserProfile
from credentials.serializers import CredentialDetailModelSerializer


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
        fields = ['first_name', 'last_name', 'bio', 'avatar', 'expertise']


class UserProfileDetailModelSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    credentials = CredentialDetailModelSerializer(many=True, read_only=True)
    articles_written = serializers.IntegerField(read_only=True)
    answers_accepted = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'bio', 'avatar', 'expertise', 'reputation_score',
                  'articles_written', 'answers_accepted', 'is_professional', 'credentials']

class UserProfileDeleteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'
