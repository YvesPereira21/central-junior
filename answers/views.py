from django.conf import settings
from django.core.cache import caches
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema
from answers.models import Answer
from profiles.models import UserProfile
from answers.serializers import AnswerModelSerializer, AnswerDetailModelSerializer, AnswerSolutionedModelSerializer
from profiles.permissions import IsOwnerQuestion


cache_view = caches['view_cache']

@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerCreateView(generics.CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerModelSerializer

    def perform_create(self, serializer):
        get_user = self.request.user
        author = UserProfile.objects.get(user=get_user)

        if author:
            serializer.save(author=author)

class AnswerListView(generics.ListAPIView):
    serializer_class = AnswerModelSerializer
    permission_classes = [IsAuthenticated]
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
class AnswerDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerDetailModelSerializer

@extend_schema(
    tags=['Answer (Resposta)']
)
class AnswerSolutionedView(generics.UpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSolutionedModelSerializer
    permission_classes = [IsAuthenticated, IsOwnerQuestion]
