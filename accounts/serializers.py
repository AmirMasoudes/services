from rest_framework import serializers
from .models import UsersModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersModel
        fields = ['id', 'id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class InputUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersModel
        fields = ['id_tel', 'username_tel', 'full_name', 'telegram_id', 'username'] 