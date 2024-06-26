from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from .models import CustomUser
from .serializers import CustomUserSerializer
from .helpers import get_tokens_for_user, generate_random_password


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


@api_view(['POST'])
def reset_password(request):
    if request.method == 'POST':
        email = request.data.get('email')

        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            return Response({'error': 'Пользователь с таким email не найден'}, status=status.HTTP_404_NOT_FOUND)

        new_password = generate_random_password()
        user.set_password(new_password)
        user.save()

        send_mail(
            'Сброс пароля',
            f'Ваш новый пароль: {new_password}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Письмо с новым паролем отправлено'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def logout_user(request):
    logout(request)
    return Response({'message': 'User logged out successfully.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_user_photo(request):
    user_id = request.data.get('id')
    avatar = request.data.get('avatar')

    if not user_id or not avatar:
        return Response({'error': 'ID пользователя и фото являются обязательными полями'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
        user.avatar = avatar
        user.save()

        user_return = CustomUserSerializer(user)
        return Response(user_return.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        raise NotFound('Пользователь с указанным ID не найден')
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def change_password(request):
    user_id = request.data.get('id')
    password = request.data.get('password')
    new_password = request.data.get('newPassword')

    if not (user_id and password and new_password):
        return Response({'error': 'ID пользователя, текущий и новый пароли являются обязательными полями'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
        if not check_password(password, user.password):
            return Response({'error': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()

        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Пользователь с указанным ID не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def change_email(request):
    user_id = request.data.get('id')
    new_email = request.data.get('newEmail')

    if not (user_id and new_email):
        return Response({'error': 'ID пользователя и новый email являются обязательными полями'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
        if not user:
            return Response({'error': 'Пользователь с указанным ID не найден'}, status=status.HTTP_404_NOT_FOUND)

        if CustomUser.objects.exclude(id=user_id).filter(email=new_email).exists():
            return Response({'error': 'Пользователь с таким email уже существует'}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.save()

        return Response({'message': 'Email успешно изменен'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
