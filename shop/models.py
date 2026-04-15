from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá bán mặc định")
    available = models.BooleanField(default=True, verbose_name="Còn hàng")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_min_variant_price(self):
        variant = self.variants.order_by('price').first()
        if variant:
            return variant.price
        return self.price

    def get_sale_info(self):
        variants = self.variants.all()
        min_price = self.price
        sale_price = None

        for v in variants:
            if v.sale_price and (sale_price is None or v.sale_price < sale_price):
                sale_price = v.sale_price
            elif not sale_price and v.price < min_price:
                min_price = v.price

        if sale_price:
            discount_percent = int((self.price - sale_price) / self.price * 100)
            return {
                'is_sale': True,
                'final_price': sale_price,
                'percent': discount_percent
            }

        return {
            'is_sale': False,
            'final_price': self.price,
            'percent': 0
        }


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Sản phẩm")
    color_name = models.CharField(max_length=50, verbose_name="Màu sắc")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá cho màu này")
    sale_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    stock = models.IntegerField(default=0, verbose_name="Số lượng trong kho")
    available = models.BooleanField(default=True, verbose_name="Còn hàng")

    class Meta:
        verbose_name = "Biến thể sản phẩm"
        verbose_name_plural = "Biến thể sản phẩm"

    def __str__(self):
        return f"{self.product.name} - Màu: {self.color_name} ({self.price} VND)"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5 sao
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"


class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField()  # ví dụ: 10 = 10%
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code