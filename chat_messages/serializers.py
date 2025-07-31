from rest_framework import serializers
from .models import MessageDirectory, MessageModel
from accounts.serializers import UserSerializer

class DirectorySerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageDirectory
        fields = ['id', 'admin', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    directory = DirectorySerializer(read_only=True)
    
    class Meta:
        model = MessageModel
        fields = ['id', 'directory', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at'] 