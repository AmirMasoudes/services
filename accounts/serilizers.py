from rest_framework import serializers
from .models import UsersModel

class InputUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersModel
        fields = ["id_tel", "username_tel", "full_name"]

    def validate_id_tel(self, value):
        if UsersModel.objects.filter(id_tel=value).exists():
            raise serializers.ValidationError("This user already exists.")
        return value
