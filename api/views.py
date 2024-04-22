from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from userauth.models import CustomUser
from .models import Article, Course, CourseStage, CourseProgress
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactUsSerializer, ArticleSerializer, ArticleSearchSerializer, ContactFAQSerializer, \
    CourseSerializer
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
    latest_news = Article.objects.order_by('-publication_date')[:5]

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


@api_view(['POST'])
def contact_faq(request):
    serializer = ContactFAQSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        subject = serializer.validated_data.get('subject')
        message = serializer.validated_data.get('message')
        try:
            send_mail(
                subject=f"EducateMe: {subject}",
                message="We have received your message, and will contact you soon",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )

            send_mail(
                subject=f"EducateMe: {subject}",
                message=f'from: {email}\n\n{message}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
        except Exception as exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_courses(request):
    try:
        sort_by = request.GET.get('sort_by', '')
        complexity = request.GET.get('complexity', '')
        topic = request.GET.get('topic', '')
        title = request.GET.get('title', '')

        courses = Course.objects.all()
        if sort_by:
            if sort_by == 'oldest':
                courses = courses.order_by('date_created')
            elif sort_by == 'newest':
                courses = courses.order_by('-date_created')
        if complexity:
            courses = courses.filter(complexity=complexity)
        if topic:
            courses = courses.filter(topic=topic)
        if title:
            courses = courses.filter(Q(title__icontains=title))

        topics = Course.objects.values_list('topic', flat=True).distinct()

        serializer = CourseSerializer(courses, many=True)
        data = {
            'courses': serializer.data,
            'topics': list(topics)
        }
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_course_info(request):
    try:
        course_id = request.GET.get('id')
        course = Course.objects.get(id=course_id)
        stages = CourseStage.objects.filter(course=course).order_by('order')
        print('course_id', course_id)
        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'image': course.image,
            'topic': course.topic,
            'complexity': course.complexity,
            'publication_date': course.publication_date,

        }

        stages_data = [{'title': stage.title, 'description': stage.description} for stage in stages]

        response_data = {
            'course': course_data,
            'stages': stages_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_course_added(request):
    course_id = request.GET.get('course_id')
    user_id = request.GET.get('user_id')

    if not course_id or not user_id:
        return Response({"error": "Both 'course_id' and 'user_id' must be provided."}, status=400)

    try:
        course_id = int(course_id)
        user_id = int(user_id)
    except ValueError:
        return Response({"error": "Invalid 'course_id' or 'user_id'. Must be integers."}, status=400)

    course_added = CourseProgress.objects.filter(user_id=user_id, course_id=course_id).exists()

    return Response(course_added)


@api_view(['POST'])
def user_add_course(request):
    user_id = request.data.get('user_id')
    course_id = request.data.get('course_id')

    if not user_id or not course_id:
        return JsonResponse({'message': 'Missing user_id or course_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=user_id)
        course = Course.objects.get(pk=course_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Course.DoesNotExist:
        return JsonResponse({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if CourseProgress.objects.filter(user=user, course=course).exists():
        return JsonResponse({'message': 'User has already added this course'}, status=status.HTTP_409_CONFLICT)

    try:
        first_stage = CourseStage.objects.filter(course=course, order=0).first()
        if not first_stage:
            return JsonResponse({'message': 'No initial stage found for this course'}, status=status.HTTP_404_NOT_FOUND)
    except CourseStage.DoesNotExist:
        return JsonResponse({'message': 'Error finding the initial stage'}, status=status.HTTP_404_NOT_FOUND)
    CourseProgress.objects.create(user=user, course=course, current_stage=first_stage)

    return JsonResponse({'message': 'Course added successfully with initial stage set'}, status=status.HTTP_200_OK)