from django.contrib import admin
from .models import Category, Product, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1 # Hiện sẵn 1 dòng để thêm màu nhanh

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available'] # Sửa nhanh giá ngoài danh sách
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline] # Thêm/Sửa màu ngay trong trang sản phẩm