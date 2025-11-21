from rest_framework import serializers
from django.utils import timezone
from app.exceptions import InvalidData, CredentialAlreadyAccepted
from credentials.models import Credential


class CredentialModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credential
        fields = ['role', 'type_credential', 'experience', 'institution', 'start_date', 'end_date']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        experience = attrs.get('experience')
        if start_date and start_date > timezone.now().date():
            raise InvalidData()

        if start_date and end_date:
            if start_date > end_date:
                raise InvalidData()

        if experience not in ['JR', 'PL', 'SR']:
            raise InvalidData()

        return attrs

class CredentialDetailModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credential
        fields = '__all__'

class CredentialUpdateModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credential
        fields = ['role', 'type_credential', 'experience', 'institution']

    def validate(self, attrs):
        if self.instance and self.instance.is_verified:
            raise CredentialAlreadyAccepted

        return attrs

class CredentialVerifiedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credential
        fields = ['is_verified']
