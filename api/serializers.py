from rest_framework import serializers
from .models import Article, CourseStage, Course, CourseProgress


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


class ContactFAQSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()


class CourseStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStage
        fields = ['title', 'description', 'image', 'text', 'publication_date', 'order']


class CourseSerializer(serializers.ModelSerializer):
    stages = CourseStageSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'topic', 'complexity', 'publication_date', 'stages']


class CourseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['topic']


class CourseProgressMenuSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseProgress
        fields = ['course', 'current_stage', 'completed']


class CourseProgressSerializer(serializers.ModelSerializer):
    current_stage = serializers.IntegerField(source='current_stage.order')

    class Meta:
        model = CourseProgress
        fields = ['course', 'current_stage', 'completed']