from rest_framework import serializers
from .models import ConfingPlansModel

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfingPlansModel
        fields = ['id', 'name', 'price', 'in_volume', 'created_at']
        read_only_fields = ['id', 'created_at'] 