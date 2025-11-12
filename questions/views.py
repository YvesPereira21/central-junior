from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from questions.models import Question
from questions.serializers import QuestionModelSerializer, QuestionDetailModelSerializer, QuestionSolutionedModelSerializer, QuestionDeleteModelSerializer
from profiles.models import UserProfile
from profiles.permissions import IsOwner


@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionCreateView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        get_user = self.request.user
        get_profile = UserProfile.objects.get(user=get_user)

        if get_profile:
            serializer.save(profile=get_profile)

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    http_method_names = ['get', 'patch', 'options', 'head']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOwner()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return QuestionDeleteModelSerializer

        return QuestionDetailModelSerializer

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionSolutionedView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSolutionedModelSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['patch', 'options', 'head']

@extend_schema(
    tags=['Question (Pergunta)']
)
class QuestionLikeToggleView(generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.Serializer
    
    def post(self, request, *args,**kwargs):
        question = self.get_object()

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({"errors": 'Usuário não possui um perfil para dar like'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        if profile in question.likes.all():
            question.likes.remove(profile)

        else:
            question.likes.add(profile)
        
        return Response({"likes_count": question.likes.count()}, 
                        status=status.HTTP_200_OK)
