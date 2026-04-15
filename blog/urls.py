from django.urls import path
from . import views

# BẮT BUỘC phải có dòng này để khớp với namespace='blog' ở file tổng
app_name = 'blog' 

urlpatterns = [
    path('', views.list, name='list'),
    path('<int:id>/', views.post, name='post'),
    path('add/', views.add_blogs, name='add_blogs'),
    path('register/', views.register, name='register'),
]