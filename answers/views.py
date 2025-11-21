from django.conf import settings
from django.core.cache import caches
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema
from answers.models import Answer
from profiles.models import UserProfile
from answers.serializers import AnswerModelSerializer, AnswerDetailModelSerializer, AnswerSolutionedModelSerializer, AnswerUpdateModelSerializer
from profiles.permissions import IsOwner, IsOwnerQuestion


cache_view = caches['view_cache']


@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerCreateView(generics.CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerModelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        get_user = self.request.user
        author = UserProfile.objects.get(user=get_user)

        if author:
            serializer.save(author=author)


@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerListView(generics.ListAPIView):
    serializer_class = AnswerModelSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering = ['created_at']

    def get_queryset(self):
        question = self.kwargs.get('question_pk')
        return Answer.objects.filter(question__pk=question.pk)

    def list(self, request, *args, **kwargs):
        question = self.kwargs.get('question_pk')
        key = f"answers_question_list_{question}"
        cached_data = cache_view.get(key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache_view.set(key, response.data, timeout=settings.CACHE_TTL)

        return response


@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerDetailDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    http_method_names = ['patch', 'delete', 'get', 'options', 'head']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]

        return [IsAuthenticated(), IsOwner()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AnswerDetailModelSerializer

        return AnswerUpdateModelSerializer


@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerAcceptView(generics.UpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSolutionedModelSerializer
    permission_classes = [IsAuthenticated, IsOwnerQuestion]
    http_method_names = ['patch', 'options', 'head']
