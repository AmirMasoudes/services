from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import UsersModel
from .serializers import UserSerializer

class UserListView(generics.ListAPIView):
    queryset = UsersModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveAPIView):
    queryset = UsersModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
