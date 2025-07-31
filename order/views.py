from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import OrderUserModel, PayMentModel
from .serializers import OrderSerializer, PaymentSerializer

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OrderUserModel.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    queryset = OrderUserModel.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PayMentModel.objects.filter(user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    queryset = PayMentModel.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
