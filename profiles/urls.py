from django.urls import path
from profiles.views import UserProfileCreateView, UserProfileDetailUpdateDeleteView


urlpatterns = [
    path('profiles/', UserProfileCreateView.as_view(), name='create-profile'),
    path('profiles/<int:pk>/', UserProfileDetailUpdateDeleteView.as_view(), name='details-profile')
]
