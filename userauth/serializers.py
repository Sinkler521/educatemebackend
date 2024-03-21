from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}


class LoginResponseSerializer(serializers.Serializer):
    user = CustomUserSerializer()
    token = serializers.CharField()