from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from articles.models import Article
from technologies.models import Technology
from technologies.serializers import TechnologyModelSerializer


class ArticleModelSerializer(serializers.ModelSerializer):
    technologies = serializers.PrimaryKeyRelatedField(
        queryset=Technology.objects.all(),
        many=True
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'technologies']


class ArticleDetailModelSerializer(serializers.ModelSerializer):
    profile_name1 = serializers.CharField(source='author.user.first_name')
    profile_name2 = serializers.CharField(source='author.user.last_name')
    technologies = TechnologyModelSerializer(many=True, read_only=True)
    quantity_likes = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['title', 'content', 'profile_name1', 'profile_name2', 'technologies', 'created_at', 'quantity_likes']

    @extend_schema_field(serializers.IntegerField())
    def get_quantity_likes(self, obj):
        return obj.likes.count()
