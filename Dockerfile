FROM python:3.12
LABEL authors="Dream Machines"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENV FRONTEND_PORT=3000
ENV EMAIL_HOST=smtp.mailersend.net
ENV EMAIL_HOST_USER=MS_Aj00FX@trial-7dnvo4d35e3g5r86.mlsender.net
ENV EMAIL_HOST_PASSWORD=rXIq1dpYxIAfuXYW
ENV EMAIL_PORT=587
ENV ADMIN_EMAIL=Sinkler521@gmail.com

RUN python manage.py collectstatic --no-input && python manage.py makemigrations && python manage.py makemigrations userauth && python manage.py migrate && python manage.py migrate userauth && echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')" | python manage.py shell

CMD python manage.py runserver 0.0.0.0:8000
