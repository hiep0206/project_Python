from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/<str:variant_id>/',views.cart_remove,name='cart_remove'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/variants/', views.get_variant_list, name='api_variants'),
    path('wishlist/<int:product_id>/', views.toggle_wishlist, name='wishlist'),
    path('apply-voucher/', views.apply_voucher, name='apply_voucher'),
]