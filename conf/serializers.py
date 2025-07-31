from rest_framework import serializers
from .models import ConfigUserModel
from accounts.serializers import UserSerializer
from order.serializers import OrderSerializer

class ConfigSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = ConfigUserModel
        fields = ['id', 'user', 'order', 'config', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
