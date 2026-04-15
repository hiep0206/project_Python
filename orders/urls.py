from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('checkout-from-cart/', views.checkout_from_cart, name='checkout_from_cart'),
    # Đường dẫn quan trọng nhất cho trang Đơn hàng của tôi
    path('my-orders/', views.order_list, name='order_list'),
]