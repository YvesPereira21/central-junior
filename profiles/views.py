from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from profiles.models import UserProfile
from profiles.serializers import UserProfileModelSerializer, UserProfileUpdateModelSerializer, UserProfileDetailModelSerializer, UserProfileDeleteModelSerializer
from profiles.permissions import IsOwner


@extend_schema(
    tags=['Profile (Perfil)']
)
class UserProfileCreateView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileModelSerializer

@extend_schema(
    tags=['Profile (Perfil)']
)
class UserProfileDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    http_method_names = ['get', 'put', 'delete', 'options', 'head']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileDetailModelSerializer

        elif self.request.method == 'DELETE':
            return UserProfileDeleteModelSerializer

        return UserProfileUpdateModelSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]

        return [IsAuthenticated(), IsOwner()]
