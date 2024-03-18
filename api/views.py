import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
def contactus(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        message = data.get('message')
        if email and message:
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
                return JsonResponse({'status': 'success', 'message': f'Something went wrong\n{e}'})
            return JsonResponse({'status': 'success', 'message': 'Message sent'})
        else:
            return JsonResponse({'status': 'failed', 'error': 'Missing data'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'failed', 'error': 'Invalid JSON data'})

