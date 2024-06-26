from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from userauth.models import CustomUser
from .models import Article, Course, CourseStage, CourseProgress
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ContactUsSerializer, ArticleSerializer, ArticleSearchSerializer, ContactFAQSerializer, \
    CourseSerializer, CourseProgressSerializer, CourseStageSerializer, CourseProgressMenuSerializer, \
    CourseTopicSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
import re


@api_view(['GET'])
def get_topics(request):
    try:
        courses = Course.objects.all()
        serialized = CourseTopicSerializer(courses, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
def get_statistics(request):
    num_custom_users = CustomUser.objects.count()
    num_completed_courses = CourseProgress.objects.filter(completed=100).count()
    num_courses = Course.objects.count()

    return Response({
        'custom_user_data': num_custom_users,
        'completed_courses_data': num_completed_courses,
        'courses_data': num_courses
    })


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
                courses = courses.order_by('publication_date')
            elif sort_by == 'newest':
                courses = courses.order_by('-publication_date')
        if complexity:
            courses = courses.filter(complexity__icontains=complexity)
        if topic:
            courses = courses.filter(topic__icontains=topic)
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
        user_id = request.GET.get('user_id')
        course = Course.objects.get(id=course_id)
        stages = CourseStage.objects.filter(course=course).order_by('order')

        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'image': course.image,
            'topic': course.topic,
            'complexity': course.complexity,
            'publication_date': course.publication_date,

        }

        stages_data = [{'title': stage.title,
                        'description': stage.description,
                        'image': stage.image,
                        'video': stage.video,
                        'text': stage.text,
                        'order': stage.order} for stage in stages]

        response_data = {
            'course': course_data,
            'stages': stages_data,
        }

        if user_id:
            user = CustomUser.objects.get(id=user_id)
            user_progress = CourseProgress.objects.filter(user=user, course=course).first()
            if user_progress:
                progress_serializer = CourseProgressSerializer(user_progress)
                progress_data = progress_serializer.data
                response_data['progress'] = progress_data

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


@api_view(['GET'])
def admin_get_info(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        courses = Course.objects.filter(teacher__id=user_id)
        if courses.exists():
            course_serializer = CourseSerializer(courses, many=True)
            courses_data = course_serializer.data

            topics_count = courses.values('topic').annotate(count=Count('topic')).order_by('-count')
            most_popular_topic = topics_count[0]['topic'] if topics_count else ''
            different_topics_count = len(topics_count)

            return Response({
                'courses': courses_data,
                'most_popular': most_popular_topic,
                'different_topics': different_topics_count
            })
        else:
            return Response({
                'courses': [],
                'most_popular': '',
                'different_topics': 0
            })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def admin_delete_course(request):
    user_id = request.query_params.get('user_id')
    course_id = request.query_params.get('course_id')
    course_title = request.query_params.get('coursetitle')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=400)

    course = get_object_or_404(Course, id=course_id)

    if course.title != course_title:
        return Response({'error': 'Incorrect course title'}, status=400)

    course.delete()
    CourseStage.objects.filter(course_id=course_id).delete()

    return Response({'message': 'Course and its stages have been deleted successfully'}, status=200)


@api_view(['POST'])
def admin_add_course(request):
    try:
        new_course_data = request.data['course']
        new_course_stages_data = request.data['stages']
        teacher_id = request.data['user_id']

        teacher = get_object_or_404(CustomUser, id=teacher_id)

        new_course = Course.objects.create(
            title=new_course_data['title'],
            description=new_course_data['description'],
            image=new_course_data['image'],
            topic=new_course_data['topic'],
            complexity=new_course_data['complexity'],
            teacher=teacher
        )
        for stage_data in new_course_stages_data:
            CourseStage.objects.create(
                course=new_course,
                title=stage_data['title'],
                description=stage_data['description'],
                image=stage_data['image'],
                video=stage_data['video'],
                text=stage_data['text'],
                order=stage_data['order']
            )

        return Response({'message': 'Course and its stages have been added successfully'},
                        status=status.HTTP_201_CREATED)

    except KeyError:
        return Response({'error': 'Invalid request data format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def user_get_courses(request):
    user_id = request.query_params.get('user_id')

    user_courses_progress = CourseProgress.objects.filter(user_id=user_id)
    serializer = CourseProgressMenuSerializer(user_courses_progress, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def user_search_courses(request):
    user_id = request.query_params.get('user_id')
    topic = request.query_params.get('topic', '')
    complexity = request.query_params.get('complexity', '')
    sortby = request.query_params.get('sortby', '')
    title = request.query_params.get('title', '')

    filters = {}
    if topic:
        filters['course__topic'] = topic
    if complexity:
        filters['course__complexity__icontains'] = complexity

    user_course_progresses = CourseProgress.objects.filter(user_id=user_id)
    if filters:
        user_course_progresses = user_course_progresses.filter(**filters)
    if title:
        user_course_progresses = user_course_progresses.filter(Q(course__title__icontains=title))

    courses_data = []
    for progress in user_course_progresses:
        course_data = {
            'course': CourseSerializer(progress.course).data,
            'stages': CourseStageSerializer(progress.course.stages.all(), many=True).data
        }
        courses_data.append(course_data)

    if sortby == 'newest':
        courses_data = sorted(courses_data, key=lambda x: x['course']['publication_date'], reverse=True)
    elif sortby == 'oldest':
        courses_data = sorted(courses_data, key=lambda x: x['course']['publication_date'])

    return Response(courses_data)


@api_view(['POST'])
def user_complete_stage(request):
    try:
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        stage_order = request.data['new_stage_order']

        user_progress = CourseProgress.objects.get(user_id=user_id, course_id=course_id)
        total_stages = CourseStage.objects.filter(course_id=course_id).count()

        if stage_order >= total_stages:
            user_progress.completed = 100
            user_progress.save()
            return Response({'error': 'User has already completed all stages of the course'},
                            status=status.HTTP_400_BAD_REQUEST)
        stage = CourseStage.objects.get(course_id=course_id, order=stage_order)

        user_progress.current_stage = stage
        user_progress.save()

        total_stages = CourseStage.objects.filter(course_id=course_id).count()
        completed_stages = CourseStage.objects.filter(course_id=course_id, order__lte=stage.order - 1).count()
        completed_percentage = round(completed_stages / total_stages * 100)

        user_progress.completed = completed_percentage
        user_progress.save()

        return Response(status=status.HTTP_200_OK)
    except CourseProgress.DoesNotExist:
        return Response({'error': 'Course progress not found'}, status=status.HTTP_404_NOT_FOUND)
    except CourseStage.DoesNotExist:
        return Response({'error': 'Course stage not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search_info(request):
    search_value = request.GET.get('searchvalue')

    if not search_value:
        return JsonResponse({'error': 'Search value is required'}, status=status.HTTP_400_BAD_REQUEST)

    course_results = Course.objects.filter(Q(title__icontains=search_value) | Q(description__icontains=search_value))
    course_data = [{'title': f'Course: {course.title}', 'link': f'/app/products/courses/{course.id}'} for course in
                   course_results]

    article_results = Article.objects.filter(Q(title__icontains=search_value) | Q(description__icontains=search_value))
    article_data = [{'title': f'Article: {article.title}', 'link': f'/app/news/{article.id}'} for article in
                    article_results]

    search_results = course_data + article_data

    return JsonResponse(search_results, safe=False)
