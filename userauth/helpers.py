from rest_framework_simplejwt.tokens import RefreshToken
import random
import string


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length - 2))
    password += random.choice(string.digits)
    password += random.choice(string.digits)
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)
