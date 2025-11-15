from django.urls import path
from articles.views import ArticleListCreateView, ArticleDetailDeleteView, ArticleToggleView


urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='create-article'),
    path('articles/<int:pk>/', ArticleDetailDeleteView.as_view(), name='article-details'),
    path('articles/<int:pk>/like/', ArticleToggleView.as_view(), name='like-article')
]
