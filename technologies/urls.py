from django.urls import path
from technologies.views import TechnologyCreateView, TechnologyRetrieveUpdateDestroyView


urlpatterns = [
    path('tags/', TechnologyCreateView.as_view(), name='technology-create'),
    path('tags/<int:pk>/', TechnologyRetrieveUpdateDestroyView.as_view(), name='technology-detail'),
]
