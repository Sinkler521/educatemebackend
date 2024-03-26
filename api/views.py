from rest_framework.decorators import api_view

from .models import Article
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactUsSerializer, ArticleSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


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
    latest_news = Article.objects.filter(publication_date__gte=seven_days_ago)

    serialized_news = ArticleSerializer(latest_news, many=True)

    return Response(serialized_news.data)


@api_view(['POST'])
def article_add(request):
    ...
