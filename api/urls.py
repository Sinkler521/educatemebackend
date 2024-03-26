from django.urls import path
from .views import *

urlpatterns = [
    path('contactus/', ContactUsView.as_view(), name='contactus'),
    path('getlatestnews/', get_latest_news, name='latest_news'),
    path('articleadd/', article_add, name='add_article'),
]