from decimal import Decimal
from django.conf import settings
from .models import Product, ProductVariant

class Cart:
    def apply_discount(self, discount_amount):
        """
        Áp dụng giảm giá cho toàn bộ giỏ hàng.
        discount_amount: số tiền giảm
        """
        self.session['cart_discount'] = str(discount_amount)
        self.save()

    def get_discount(self):
        return Decimal(self.session.get('cart_discount', '0'))

    def get_total_price_after_discount(self):
        total = self.get_total_price()
        discount = self.get_discount()
        return total - discount

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, variant_id='0', quantity=1, override_quantity=False):
        # Tạo key duy nhất để phân biệt màu sắc: ví dụ "5_2" (Sản phẩm 5, màu 2)
        item_key = f"{product.id}_{variant_id}"
        
        if item_key not in self.cart:
            # Lấy giá và màu sắc thực tế
            price = product.price
            color_name = "Tiêu chuẩn"
            if variant_id != '0' and variant_id != '':
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    price = variant.price
                    color_name = variant.color_name
                except ProductVariant.DoesNotExist:
                    pass
            
            self.cart[item_key] = {
                'quantity': 0,
                'price': str(price),
                'color': color_name,
                'variant_id': variant_id
            }

        if override_quantity:
            self.cart[item_key]['quantity'] = int(quantity)
        else:
            self.cart[item_key]['quantity'] += int(quantity)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product_id, variant_id='0'):
        item_key = f"{product_id}_{variant_id}"
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def __iter__(self):
        # Lặp qua giỏ hàng để hiển thị ra Template
        for item_key, item in self.cart.items():
            p_id = item_key.split('_')[0]
            product = Product.objects.get(id=p_id)
            
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['item_key'] = item_key
            item['v_id'] = item_key.split('_')[1] # Để dùng cho nút xóa
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()