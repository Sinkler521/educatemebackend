from rest_framework import serializers
from .models import Article


class ContactUsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class ArticleSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField()

    def validate_search_query(self, value):
        if not value.strip():
            raise serializers.ValidationError("Search query cannot be empty")
        return value