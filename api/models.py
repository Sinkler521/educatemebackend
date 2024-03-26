from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    image = models.TextField()  # base64 will be used, so
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title