from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password

from .models import CustomUser
from .serializers import CustomUserSerializer
from .helpers import get_tokens_for_user


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            if CustomUser.objects.filter(email=email).exists() or CustomUser.objects.filter(username=username).exists():
                return Response({'error': 'Пользователь с таким email или username уже существует.'}, status=status.HTTP_409_CONFLICT)

            CustomUser.objects.create_user(email=email, username=username, password=password)
            return Response({'message': 'Пользователь успешно зарегистрирован.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user is not None:
            if check_password(password, user.password):
                login(request, user)
                tokens = get_tokens_for_user(user)
                serialized_user = CustomUserSerializer(user)
                response_data = {'user': serialized_user.data, 'token': tokens['access']}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неправильный пароль'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Пользователь с таким email не существует'}, status=status.HTTP_404_NOT_FOUND)
