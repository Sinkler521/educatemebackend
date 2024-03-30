from django.urls import path
from .views import *

urlpatterns = [
    path('contactus/', ContactUsView.as_view(), name='contactus'),
    path('getlatestnews/', get_latest_news, name='latest_news'),
    path('getallnews/', get_all_news, name='get_all_news'),
    path('searchnews/', search_news, name='search_news'),
    path('articleadd/', article_add, name='add_article'),
    path('articleget/<int:article_id>/', article_get, name='article_get'),
    path('articlechange/', article_change, name='article_change')
]