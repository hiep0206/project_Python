from django.contrib import admin
from .models import Post # Blog thường dùng bảng Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    search_fields = ['title']