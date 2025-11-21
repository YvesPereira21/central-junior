from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from profiles.models import UserProfile
from profiles.serializers import UserProfileModelSerializer, UserProfileUpdateModelSerializer, UserProfileDetailModelSerializer, UserProfileDeleteModelSerializer
from profiles.permissions import IsOwner


@extend_schema(
    tags=['Profile (Perfil)']
)
class UserProfileCreateView(generics.CreateAPIView):
    serializer_class = UserProfileModelSerializer

    def get_queryset(self):
        return UserProfile.objects.all().annotate(
            articles_written=Count('article_author', distinct=True),
            answers_accepted=Count('answer_author',
                                   filter=Q(answer_author__is_accepted=True),
                                   distinct=True)
        )


@extend_schema(
    tags=['Profile (Perfil)']
)
class UserProfileDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'put', 'patch', 'delete', 'options', 'head']

    def get_queryset(self):
        return UserProfile.objects.all().annotate(
            articles_written=Count('article_author', distinct=True),
            answers_accepted=Count('answer_author',
                                   filter=Q(answer_author__is_accepted=True),
                                   distinct=True)
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileDetailModelSerializer

        elif self.request.method == 'DELETE':
            return UserProfileDeleteModelSerializer

        return UserProfileUpdateModelSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwner()]

    @method_decorator(cache_page(settings.CACHE_TTL, cache='view_cache', key_prefix='detail_profile'))
    @method_decorator(vary_on_headers('Authorization'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
