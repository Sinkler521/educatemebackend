from django.urls import path
from .views import *

urlpatterns = [
    path('gettopics/', get_topics, name='get_topics'),
    path('contactus/', ContactUsView.as_view(), name='contactus'),
    path('getstatistics/', get_statistics, name='get_statistics'),
    path('getlatestnews/', get_latest_news, name='latest_news'),
    path('getallnews/', get_all_news, name='get_all_news'),
    path('searchnews/', search_news, name='search_news'),
    path('articleadd/', article_add, name='add_article'),
    path('articleget/<int:article_id>/', article_get, name='article_get'),
    path('articlechange/', article_change, name='article_change'),
    path('articledelete/', article_delete, name='article_delete'),
    path('contactfaq/', contact_faq, name='contact_faq'),

    path('getcourses/', get_courses, name='get_courses'),
    path('getcourseinfo/', get_course_info, name='get_course_info'),
    path('checkcourseadded/', check_course_added, name='check_course_added'),
    path('useraddcourse/', user_add_course, name='user_add_course'),
    path('searchinfo/', search_info, name='search_info'),

    path('admingetinfo/', admin_get_info, name='admin_get_info'),
    path('admindeletecourse/', admin_delete_course, name='admin_delete_course'),
    path('adminaddcourse/', admin_add_course, name='admin_add_course'),
    path('getmycourses/', user_get_courses, name='user_get_courses'),
    path('searchmycourses/', user_search_courses, name='user_search_courses'),
    path('usercompletestage/', user_complete_stage, name='user_complete_stage')
]
