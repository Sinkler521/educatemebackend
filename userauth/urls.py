from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('resetpassword/', reset_password, name='reset_password'),
    path('logout/', logout_user, name='logout_user'),
]