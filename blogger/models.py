from django.db import models

# Kiểm tra xem tên class có đúng là 'Post' (viết hoa chữ P) không
class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title