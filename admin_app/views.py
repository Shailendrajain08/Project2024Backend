from rest_framework import viewsets, status
from .serializers import DashboardSerializer,AdminLoginSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin
from accounts.views import LoginViewSet


class AdminDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ["get", "head", "options"]
    
    def get_queryset(self):
        """
        Returns None queryset.

        Since the data is dynamically generated and serialized in the serializer, and not retrieved
        from a queryset associated with a model, we return None to indicate that there is no queryset
        associated with this viewset.
        """
        return None

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        data = serializer.to_representation(serializer.instance)
        return Response(data)

   
class AdminLoginViewSet(LoginViewSet):
    serializer_class = AdminLoginSerializer
    http_method_names = ["post", "head", "options"]

    
  