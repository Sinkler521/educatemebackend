from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    image = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    image = models.TextField()
    topic = models.CharField(max_length=16)
    complexity = models.CharField(max_length=12)
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseStage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    image = models.TextField()
    text = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title
