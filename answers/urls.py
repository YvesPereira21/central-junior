from django.urls import path
from answers.views import AnswerCreateView, AnswerDetailDeleteView, AnswerAcceptView


urlpatterns = [
    path('answers/', AnswerCreateView.as_view(), name='create-answer'),
    path('answers/<int:pk>/', AnswerDetailDeleteView.as_view(), name='answer-details'),
    path('answers/<int:pk>/accept/', AnswerAcceptView.as_view(), name='answer-accept')
]
