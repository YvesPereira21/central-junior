from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import extend_schema
from technologies.models import Technology
from technologies.serializers import TechnologyModelSerializer, TechnologyDetailUpdateDeleteModelSerializer


@extend_schema(
    tags=['Technology (Tecnologia)']
)
class TechnologyCreateView(generics.CreateAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyModelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

@extend_schema(
    tags=['Technology (Tecnologia)']
)
class TechnologyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyDetailUpdateDeleteModelSerializer
    http_method_names = ['get', 'put', 'delete', 'options', 'head']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsAdminUser()]
