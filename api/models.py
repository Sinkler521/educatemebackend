from django.db import models

from userauth.models import CustomUser


class Article(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    image = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=30)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=400, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    topic = models.CharField(max_length=16)
    complexity = models.CharField(max_length=12)
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseStage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    video = models.CharField(max_length=360, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class CourseProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_progresses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progresses')
    current_stage = models.ForeignKey(CourseStage, on_delete=models.SET_NULL, null=True, blank=True, related_name='progresses')
    completed = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.completed}% complete"

    class Meta:
        unique_together = (('user', 'course'),)
