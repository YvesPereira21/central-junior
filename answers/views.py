from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from answers.models import Answer
from profiles.models import UserProfile
from answers.serializers import AnswerModelSerializer, AnswerDetailModelSerializer, AnswerSolutionedModelSerializer
from profiles.permissions import IsOwnerQuestion


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
