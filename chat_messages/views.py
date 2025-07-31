from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MessageDirectory, MessageModel
from .serializers import DirectorySerializer, MessageSerializer

class DirectoryListView(generics.ListAPIView):
    serializer_class = DirectorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MessageDirectory.objects.filter(user=self.request.user)

class DirectoryDetailView(generics.RetrieveAPIView):
    queryset = MessageDirectory.objects.all()
    serializer_class = DirectorySerializer
    permission_classes = [IsAuthenticated]

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MessageModel.objects.filter(directory__user=self.request.user)

class MessageDetailView(generics.RetrieveAPIView):
    queryset = MessageModel.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
