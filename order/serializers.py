from rest_framework import serializers
from .models import OrderUserModel, PayMentModel
from accounts.serializers import UserSerializer
from plan.serializers import PlanSerializer

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plans = PlanSerializer(read_only=True)
    
    class Meta:
        model = OrderUserModel
        fields = ['id', 'user', 'plans', 'is_active', 'start_plane_at', 'end_plane_at', 'created_at']
        read_only_fields = ['id', 'start_plane_at', 'end_plane_at', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = PayMentModel
        fields = ['id', 'user', 'order', 'images', 'code_pay', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
