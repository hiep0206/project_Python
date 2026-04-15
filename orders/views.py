
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from .forms import OrderCreateForm
from shop.models import Product, ProductVariant
from decimal import Decimal
from django.contrib.auth.decorators import login_required

def order_create(request):

    print("BUY NOW ITEM:", request.session.get('buy_now_item'))
    print("CART SESSION:", request.session.get('cart'))
    print("---- DEBUG ----")

    buy_now_item = request.session.get('buy_now_item')
    cart_session = request.session.get('cart', {})

    cart_summary = []

    total_price = 0


   # ===== BUY NOW =====
    if buy_now_item:
        cart_session = {}
        p_id = buy_now_item.get('product_id')
        v_id = buy_now_item.get('variant_id')
        quantity = int(buy_now_item.get('quantity',1))
        product = get_object_or_404(Product,id=p_id)

        if v_id and v_id != "0":
            variant = get_object_or_404(ProductVariant, id=v_id)
            # Lấy giá đã giảm nếu có
            price = Decimal(str(buy_now_item.get('discounted_price', buy_now_item.get('price', variant.price))))
            color = buy_now_item.get('color', variant.color_name)
        else:
            price = Decimal(str(buy_now_item.get('discounted_price', buy_now_item.get('price', product.price))))
            color = "Tiêu chuẩn"

        subtotal = price * quantity
        total_price = subtotal

        cart_summary.append({
            'product': product,
            'color': color,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        })

    # ===== CART =====
    else:
        for item_key, item in cart_session.items():
            try:
                product = Product.objects.get(id=item['product_id'])
                # 🔹 ưu tiên discounted_price
                price = Decimal(str(item.get('discounted_price', item.get('price', product.price))))
                color = item.get('color',"Tiêu chuẩn")
                qty = int(item.get('quantity',1))
                subtotal = price * qty
                total_price += subtotal
                cart_summary.append({
                    'product': product,
                    'color': color,
                    'quantity': qty,
                    'price': price,
                    'subtotal': subtotal
                })
            except Product.DoesNotExist:
                continue


    # ===== CREATE ORDER =====

    if request.method=='POST':

        form=OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False) 
            if request.user.is_authenticated:
                order.user = request.user 
            order.save() 

            order=form.save()

            for item in cart_summary:

                OrderItem.objects.create(

                    order=order,

                    product=item['product'],

                    price=item['price'],

                    quantity=item['quantity']

                )


            # clear session

            if buy_now_item and not cart_session:

                del request.session['buy_now_item']

            else:

                request.session['cart']={}

            request.session.modified=True

            return render(request,'orders/created.html',{'order':order})


    form=OrderCreateForm()

    return render(request,'orders/create.html',{

        'cart':cart_summary,

        'total_price':total_price,

        'form':form

    })

def checkout_from_cart(request):
    # ❗ XÓA dữ liệu mua ngay
    request.session.pop('buy_now_item', None)

    return redirect('orders:order_create')

@login_required # Chỉ ai đăng nhập mới được xem "Đơn hàng của tôi"
def order_list(request):
    # Lấy tất cả đơn hàng thuộc về user đang đăng nhập
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})