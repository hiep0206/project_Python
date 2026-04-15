from django.db import models
from shop.models import Product
from django.conf import settings

class Order(models.Model):
    # Thêm dòng này để biết đơn hàng của ai
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             on_delete=models.CASCADE, 
                             related_name='orders', 
                             null=True, blank=True)
    
    first_name = models.CharField(max_length=50, verbose_name="Họ")

class Order(models.Model):
    # Thông tin khách hàng
    first_name = models.CharField(max_length=50, verbose_name="Họ")
    last_name = models.CharField(max_length=50, verbose_name="Tên")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=250, verbose_name="Địa chỉ")
    city = models.CharField(max_length=100, verbose_name="Thành phố")
    
    # Thông tin quản lý đơn hàng
    created = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    updated = models.DateTimeField(auto_now=True, verbose_name="Cập nhật cuối")
    paid = models.BooleanField(default=False, verbose_name="Đã thanh toán")

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Các đơn hàng"

    def __str__(self):
        return f'Đơn hàng {self.id}'

    def get_total_cost(self):
        """Tính tổng tiền của cả hóa đơn"""
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    # Liên kết với bảng Order ở trên
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # Liên kết với bảng Product bên app shop
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá tại thời điểm mua")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """Tính tiền cho từng món hàng (giá x số lượng)"""
        return self.price * self.quantity