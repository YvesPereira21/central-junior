from django.urls import path
from answers.views import AnswerCreateView, AnswerDetailDeleteView, AnswerSolutionedView


urlpatterns = [
    path('answers/', AnswerCreateView.as_view(), name='create-answer'),
    path('answers/<int:pk>/', AnswerDetailDeleteView.as_view(), name='answer-details'),
    path('answers/<int:pk>/solution/', AnswerSolutionedView.as_view(), name='answer-solution')
]