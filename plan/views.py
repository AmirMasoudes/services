from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ConfingPlansModel
from .serializers import PlanSerializer

class PlanListView(generics.ListAPIView):
    queryset = ConfingPlansModel.objects.filter(is_deleted=False)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

class PlanDetailView(generics.RetrieveAPIView):
    queryset = ConfingPlansModel.objects.filter(is_deleted=False)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
