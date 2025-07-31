from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ConfigUserModel
from .serializers import ConfigSerializer

class ConfigListView(generics.ListAPIView):
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConfigUserModel.objects.filter(user=self.request.user, is_active=True)

class ConfigDetailView(generics.RetrieveAPIView):
    queryset = ConfigUserModel.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]
