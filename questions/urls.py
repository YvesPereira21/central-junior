from django.urls import path
from questions.views import QuestionListCreateView, QuestionDetailUpdateView, QuestionLikeToggleView
from answers.views import AnswerListView


urlpatterns = [
    path('questions/', QuestionListCreateView.as_view(), name='create-question'),
    path('questions/<int:pk>/', QuestionDetailUpdateView.as_view(), name='detail-question'),
    path('questions/<int:pk>/like/', QuestionLikeToggleView.as_view(), name='like-question'),
    path('questions/<int:question_pk>/answers/', AnswerListView.as_view(), name='answers-question'),
]
