from django.contrib import admin
from .models import *

admin.site.register(Article)
admin.site.register(Course)
admin.site.register(CourseStage)
admin.site.register(CourseProgress)
