from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from articles.models import Article
from articles.serializers import ArticleModelSerializer, ArticleDetailModelSerializer
from profiles.models import UserProfile
from profiles.permissions import IsOwner


@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleModelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        get_user = UserProfile.objects.get(user=user)

        if get_user:
            serializer.save(author=get_user)

@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailModelSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsOwner()]

@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleToggleView(generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        profile = request.user.profile

        if profile in article.likes.all():
            article.likes.remove(profile)

        else:
            article.likes.add(profile)
        
        return Response({"likes_count": article.likes.count()}, status=status.HTTP_200_OK)
