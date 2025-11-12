from rest_framework import serializers
from technologies.models import Technology


class TechnologyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = '__all__'

class TechnologyDetailUpdateDeleteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = '__all__'

class TechnologyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = ['name', 'logo']
