import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def contactus(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        message = data.get('message')

        if email and message:
            #

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed', 'error': 'Missing data'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'failed', 'error': 'Invalid JSON data'})

