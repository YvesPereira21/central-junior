from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import caches
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_spectacular.utils import extend_schema
from questions.models import Question
from questions.filters import QuestionFilter
from app.exceptions import ObjectNotFound
from questions.serializers import QuestionModelSerializer, QuestionDetailModelSerializer, QuestionDeleteModelSerializer, QuestionListModelSerializer
from profiles.models import UserProfile
from profiles.permissions import IsOwner


cache_view = caches['view_cache']

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.filter(is_published=True)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = QuestionFilter
    search_fields = ['title', 'content']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]

        return [AllowAny()]
    
    def get_object(self):
        obj = super().get_object()

        if not obj.is_published:
            raise ObjectNotFound()

        return obj

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionModelSerializer

        return QuestionListModelSerializer

    def perform_create(self, serializer):
        get_user = self.request.user
        get_profile = UserProfile.objects.get(user=get_user)

        if get_profile:
            serializer.save(profile=get_profile)

        cache_view.delete("list_all_question_published")

    def list(self, request, *args, **kwargs):
        key = "list_all_question_published"
        cached_data = cache_view.get(key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache_view.set(key, response.data, timeout=settings.CACHE_TTL)
        return response

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]

        return [IsAuthenticated(), IsOwner()]

    def get_object(self):
        obj = super().get_object()

        if not obj.is_published:
            raise ObjectNotFound()

        return obj

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return QuestionDeleteModelSerializer

        return QuestionDetailModelSerializer

    def retrieve(self, request, *args, **kwargs):
        question = self.get_object()
        key = f"question_detail_{question.pk}"

        cached_data = cache_view.get(key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().retrieve(request, *args, **kwargs)
        cache_view.set(key, response.data, timeout=settings.CACHE_TTL)
        return response

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionLikeToggleView(generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.Serializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args,**kwargs):
        question = self.get_object()

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return ObjectNotFound()

        if profile in question.likes.all():
            question.likes.remove(profile)
        else:
            question.likes.add(profile)
        
        return Response({"likes_count": question.likes.count()}, 
                        status=status.HTTP_200_OK)
