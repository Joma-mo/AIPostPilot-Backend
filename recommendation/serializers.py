from rest_framework import serializers
from .models import EngagementLog

class EngagementLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementLog
        fields = '__all__'
