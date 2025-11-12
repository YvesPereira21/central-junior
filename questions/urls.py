from django.urls import path
from questions.views import QuestionCreateView, QuestionDetailUpdateView, QuestionSolutionedView, QuestionLikeToggleView


urlpatterns = [
    path('questions/', QuestionCreateView.as_view(), name='create-question'),
    path('questions/<int:pk>/', QuestionDetailUpdateView.as_view(), name='detail-question'),
    path('questions/<int:pk>/solutioned/', QuestionSolutionedView.as_view(), name='solutioned-question'),
    path('questions/<int:pk>/likes/', QuestionLikeToggleView.as_view(), name='likes-question')
]
