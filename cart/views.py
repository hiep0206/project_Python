from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from shop.cart import Cart 

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    variant_id = request.POST.get('variant_id', '0')
    buy_now = request.POST.get('buy_now', 'false')
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    cart.add(product=product, variant_id=variant_id, quantity=quantity)

    # ===== FIX QUAN TRỌNG =====
    if buy_now == 'true':
        # Lưu thông tin mua ngay vào session
        request.session['buy_now_item'] = {
            'product_id': product.id,
            'variant_id': variant_id,
            'quantity': quantity,
            'price': str(product.price),
            'color': 'Tiêu chuẩn'
        }
        return redirect('orders:order_create')
    else:
        # ❗ XÓA buy_now_item nếu đi từ giỏ hàng
        if 'buy_now_item' in request.session:
            del request.session['buy_now_item']

        return redirect('shop:cart_detail')

def cart_remove(request, product_id, variant_id='0'):
    cart = Cart(request)
    cart.remove(product_id, variant_id)
    return redirect('shop:cart_detail')

