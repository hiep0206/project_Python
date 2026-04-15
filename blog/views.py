from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import RegistrationForm, BlogPostForm

# 1. Trang danh sách bài viết: http://127.0.0.1:8000/blog/
def list(request):
    posts = Post.objects.all()
    return render(request, 'blog/blog.html', {'Posts': posts})

# 2. Trang chi tiết bài viết: http://127.0.0.1:8000/blog/<id>/
def post(request, id):
    # Lấy bài viết theo ID, nếu không có sẽ tự động hiện trang lỗi 404
    post_detail = get_object_or_404(Post, id=id)
    return render(request, 'blog/post.html', {'post': post_detail})

# 3. Trang đăng ký thành viên: http://127.0.0.1:8000/blog/register/
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Tạo người dùng mới từ dữ liệu form
            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            messages.success(request, "Đăng ký thành công! Mời bạn đăng nhập.")
            return redirect('/login/') # Chuyển hướng đến trang đăng nhập hệ thống
    else:
        form = RegistrationForm()
    return render(request, 'pages/register.html', {'form': form})

# 4. Trang thêm bài viết mới: http://127.0.0.1:8000/blog/add/
@login_required(login_url='/admin/login/') # Yêu cầu đăng nhập trước khi viết bài
def add_blogs(request):
    if request.method == "POST":
        # request.FILES rất quan trọng để xử lý hình ảnh bài viết
        form = BlogPostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            blogpost = form.save(commit=False)
            blogpost.author = request.user # Tự động gán người đang đăng nhập làm tác giả
            blogpost.save()
            # Trả về trang add_blog cùng với thông báo thành công (alert=True)
            return render(request, "pages/add_blog.html", {
                'form': BlogPostForm(), # Reset form trống sau khi đăng thành công
                'alert': True
            })
    else:
        form = BlogPostForm()
    
    return render(request, "pages/add_blog.html", {'form': form})