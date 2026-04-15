from django.shortcuts import render
from .models import Post

# Phải có hàm mang tên 'list' như thế này
def list(request):
    Data = {'Posts': Post.objects.all().order_by('-date')}
    return render(request, 'blog/blog.html', Data)