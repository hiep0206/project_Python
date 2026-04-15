from django.db import models
from django.conf import settings 

class Post(models.Model):
    title = models.CharField(max_length=100)
    # Thêm null=True, blank=True để các bài cũ không bị trùng lặp lỗi UNIQUE
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title