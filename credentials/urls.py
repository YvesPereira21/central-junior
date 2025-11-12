from django.urls import path
from credentials.views import CredentialCreateView, CredentialDetailUpdateDeleteView, CredentialValidateView


urlpatterns = [
    path('credentials/', CredentialCreateView.as_view(), name='credential-create'),
    path('credentials/<int:pk>/', CredentialDetailUpdateDeleteView.as_view(), name='credential-details'),
    path('credentials/<int:pk>/validate/', CredentialValidateView.as_view(), name='credential-validate'),
]
