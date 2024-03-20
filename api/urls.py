from django.urls import path
from .views import ContactUsView

urlpatterns = [
    path('contactus/', ContactUsView.as_view(), name='contactus'),
]