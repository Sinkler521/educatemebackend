from rest_framework import serializers
from .models import Article


class ContactUsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
