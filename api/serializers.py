from rest_framework import serializers
from .models import Article
import re


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

    def search_articles(self):
        search_query = self.validated_data['value']
        title_matches = Article.objects.filter(title__iregex=r'\y{}\y'.format(re.escape(search_query)))
        description_matches = Article.objects.filter(description__iregex=r'\y{}\y'.format(re.escape(search_query)))
        articles = list(title_matches) + list(description_matches)
        return articles
