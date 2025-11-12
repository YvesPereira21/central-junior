from rest_framework import generics
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from credentials.models import Credential
from credentials.serializers import CredentialModelSerializer, CredentialUpdateModelSerializer, CredentialDetailDeleteModelSerializer, CredentialVerifiedModelSerializer
from profiles.models import UserProfile
from profiles.permissions import IsOwner


@extend_schema(
    tags=['Credential (Credencial)']
)
class CredentialCreateView(generics.CreateAPIView):
    queryset = Credential.objects.all()
    serializer_class = CredentialModelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)

        if profile:
            serializer.save(profile=profile)

@extend_schema(
    tags=['Credential (Credencial)']
)
class CredentialDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Credential.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return CredentialUpdateModelSerializer

        return CredentialDetailDeleteModelSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOwner()]

        return [IsAuthenticated(), IsOwner()]

@extend_schema(
    tags=['Credential (Credencial)']
)
class CredentialValidateView(generics.UpdateAPIView):
    queryset = Credential.objects.all()
    serializer_class = CredentialVerifiedModelSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['patch', 'options', 'head']
