from django import forms
from django.contrib.auth.models import User
from .models import Post

# Form đăng ký thành viên
class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30, label="Tên đăng nhập")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Nhập lại mật khẩu")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_password_confirm(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Mật khẩu không khớp.")
        return p2

# Form đăng bài viết (Đây là phần bạn đang thiếu gây ra lỗi)
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tiêu đề bài viết'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nội dung bài viết'}),
        }