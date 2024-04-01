from rest_framework import status
from rest_framework.decorators import api_view

from .models import Article
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactUsSerializer, ArticleSerializer, ArticleSearchSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import re


class ContactUsView(APIView):
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            message = serializer.validated_data.get('message')
            try:
                send_mail(
                    subject="EducateMe thanks for your message",
                    message="We have received your message, and will contact you soon",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False
                )

                send_mail(
                    subject="EducateMe new message",
                    message=f'from: {email}\n{message}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False
                )
            except Exception as e:
                return Response({'status': 'failed', 'error': f'Something wrong\n{e}'})
            return Response({'status': 'success', 'message': 'Message sent'})
        else:
            return Response({'status': 'failed', 'error': serializer.errors}, status=400)


@api_view(['GET'])
def get_latest_news(request):
    seven_days_ago = timezone.now() - timedelta(days=7)
    latest_news = Article.objects.filter(publication_date__gte=seven_days_ago).order_by('-publication_date')

    serialized_news = ArticleSerializer(latest_news, many=True)

    return Response(serialized_news.data)


@api_view(['GET'])
def get_all_news(request):

    news = Article.objects.all().order_by('-publication_date')
    serialized_news = ArticleSerializer(news, many=True)

    return Response(serialized_news.data)


@api_view(['POST'])
def search_news(request):
    search_query = request.data.get('value', '')

    serializer = ArticleSearchSerializer(data={'search_query': search_query})

    if serializer.is_valid():
        articles = (Article.objects.filter(title__regex=r'(?i).*' + re.escape(search_query) + r'.*')
                    .order_by('-publication_date'))
        result_serializer = ArticleSerializer(articles, many=True)
        return Response(result_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def article_add(request):

    title = request.data.get('title')
    description = request.data.get('description')
    image_base64 = request.data.get('image')

    if not title or not description or not image_base64:
        return Response({'message': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

    article = Article(title=title, description=description, image=image_base64)
    article.save()
    return Response({'message': 'Article added successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def article_get(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    except Article.DoesNotExist:
        return Response({'message': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def article_change(request):
    try:
        article_id = request.data.get('id')
        article = Article.objects.get(id=article_id)

        article.title = request.data.get('title')
        article.description = request.data.get('description')
        article.image = request.data.get('image')

        article.save()
        return Response({'message': 'Article updated successfully'}, status=status.HTTP_200_OK)
    except Article.DoesNotExist:
        return Response({'message': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def article_delete(request):
    try:
        article_id = request.data.get('id')
        article = Article.objects.get(id=article_id)

        article.delete()
        return Response({'message': 'Article deleted successfully'}, status=status.HTTP_200_OK)
    except Article.DoesNotExist:
        return Response({'message': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)
