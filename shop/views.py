from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Category, Product, ProductVariant
from .forms import RegisterForm
from django.http import JsonResponse
from .models import Review
from .forms import ReviewForm
from .models import Wishlist
from .models import Voucher
from .cart import Cart
from decimal import Decimal

# --- UTILS ---
def get_cart_data(request):
    cart = request.session.get('cart', {})
    return sum(item.get('quantity', 0) for item in cart.values())


# --- PRODUCT VIEWS ---
def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # --- Lọc theo danh mục ---
    category_slug = request.GET.get('category_select', '')
    if category_slug:
        try:
            target_category = Category.objects.get(slug=category_slug)
            products = products.filter(category=target_category)
        except Category.DoesNotExist:
            pass

    # --- Lọc theo từ khóa ---
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(name__icontains=query)

    # --- Thêm sale_info cho mỗi sản phẩm ---
    for p in products:
        p.sale_info = p.get_sale_info()

    # --- Xác định sản phẩm nổi bật (sale cao nhất) ---
    sale_products = [p for p in products if p.sale_info['is_sale']]
    featured_product = None
    if sale_products:
        featured_product = max(sale_products, key=lambda x: x.sale_info['percent'])
        # Không loại khỏi danh sách bình thường nữa
        # Chỉ đánh dấu nổi bật bằng biến featured_product

    # --- Sắp xếp các sản phẩm theo giá final_price ---
    products = sorted(products, key=lambda x: x.sale_info['final_price'])

    return render(request, 'shop/list.html', {
        'categories': categories,
        'featured_product': featured_product,
        'products': products,
        'query': query,
        'category_select': category_slug,
        'cart_count': get_cart_data(request)
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    variants = product.variants.all()
    reviews = product.reviews.all().order_by('-created')

    # Check wishlist
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Wishlist.objects.filter(user=request.user, product=product).exists()

    # Tính sale info cho biến thể
    variant_list = []
    for v in variants:
        final_price = v.sale_price if v.sale_price else v.price
        is_sale = bool(v.sale_price and v.sale_price < v.price)
        discount_percent = int((v.price - final_price) / v.price * 100) if is_sale else 0
        variant_list.append({
            'id': v.id,
            'color': v.color_name,
            'price': v.price,
            'final_price': final_price,
            'is_sale': is_sale,
            'percent': discount_percent
        })

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('shop:product_detail', id=id, slug=slug)
        else:
            return redirect('shop:login')
    else:
        form = ReviewForm()

    vouchers = Voucher.objects.filter(active=True)
    return render(request, 'shop/detail.html', {
        'product': product,
        'variants': variant_list,
        'reviews': reviews,
        'form': form,
        'is_favorite': is_favorite,
        'vouchers': vouchers,
        'cart_count': get_cart_data(request)
    })


def get_variant_list(request):

    product_id = request.GET.get('pid')

    product = get_object_or_404(Product, id=product_id)

    variants = product.variants.all()

    data = [

        {

            'id': v.id,

            'color': v.color_name,

            'price': int(v.price)

        }

        for v in variants

    ]

    return JsonResponse({'variants': data})


# ========================== CART VIEWS ==========================

def cart_detail(request):
    cart_session = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal('0')
    discount = Decimal('0')

    for item_key, item in cart_session.items():
        try:
            product = Product.objects.get(id=int(item['product_id']))
            qty = int(item.get('quantity', 0))
            # Lấy giá giảm nếu có
            price = Decimal(str(item.get('discounted_price', item.get('price', 0))))
            subtotal = price * qty
            total_price += subtotal

            cart_items.append({
                'product': product,
                'quantity': qty,
                'color': item.get('color', 'Tiêu chuẩn'),
                'price': price,
                'subtotal': subtotal,
                'item_key': item_key,
                'variant_id': item.get('variant_id')
            })
        except Product.DoesNotExist:
            continue

    # Tổng discount = tổng giá gốc - tổng giá sau giảm
    original_total = sum(Decimal(str(item.get('price', 0))) * item.get('quantity', 0) for item in cart_session.values())
    discount = original_total - total_price

    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': original_total,
        'discount': discount,
        'final_price': total_price,
        'voucher': request.session.get('voucher'),
        'cart_count': get_cart_data(request)
    })


def cart_add(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    variant_id_str = request.GET.get('variant_id')

    if not variant_id_str:
        variant_id_str = request.POST.get('variant_id', '0')

    variant_id_str = str(variant_id_str or "0")

    action = request.GET.get('action')

    buy_now = request.GET.get('buy_now')

    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})

    # Lấy giá variant
    if variant_id_str != "0":

        try:

            variant = ProductVariant.objects.get(id=int(variant_id_str))

            price = float(variant.sale_price if variant.sale_price else variant.price)

            color = variant.color_name

        except:

            price = float(product.price)

            color = "Tiêu chuẩn"

            variant_id_str = "0"

    else:

        price = float(product.price)

        color = "Tiêu chuẩn"

    item_key = f"{product_id}_{variant_id_str}"

    # ===== BUY NOW =====
    if buy_now:
        request.session['buy_now_item'] = {
            'product_id': str(product_id),
            'variant_id': variant_id_str,
            'quantity': quantity,
            'price': price,
            'discounted_price': price,  # 🔹 lưu giá đã giảm ban đầu
            'color': color
        }
        request.session.modified = True
        return redirect('orders:order_create')

    # ===== CART NORMAL =====
    if item_key not in cart:

        if action in ["plus","minus"]:

            return redirect('shop:cart_detail')

        cart[item_key] = {

            'product_id': str(product_id),

            'variant_id': variant_id_str,

            'quantity': 0,

            'price': price,

            'color': color,

            'name': product.name,

            'image': product.image.url if product.image else ''

        }

    if action == "plus":

        cart[item_key]['quantity'] += 1

    elif action == "minus":

        cart[item_key]['quantity'] -= 1

        if cart[item_key]['quantity'] <= 0:

            del cart[item_key]

    else:

        cart[item_key]['quantity'] += quantity

    request.session['cart'] = cart

    request.session.modified = True

    return redirect('shop:cart_detail')


def cart_remove(request, product_id, variant_id):

    cart = request.session.get('cart', {})

    variant_id = str(variant_id or "0")

    item_key = f"{product_id}_{variant_id}"

    if item_key in cart:

        del cart[item_key]

    old_keys = [

        str(product_id),

        f"{product_id}_None",

        f"{product_id}_"

    ]

    for k in old_keys:

        if k in cart:

            del cart[k]

    request.session['cart'] = cart

    request.session.modified = True

    return redirect('shop:cart_detail')


# --- AUTH VIEWS ---

def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data['password'])

            user.save()

            login(request, user)

            return redirect('shop:product_list')

    else:

        form = RegisterForm()

    return render(request, 'shop/register.html', {'form': form})


def login_view(request):

    if request.method == 'POST':

        form = AuthenticationForm(data=request.POST)

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect('shop:product_list')

    else:

        form = AuthenticationForm()

    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):

    logout(request)

    return redirect('shop:product_list')

def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    product = get_object_or_404(Product, id=product_id)

    item = Wishlist.objects.filter(user=request.user, product=product)

    if item.exists():
        item.delete()
    else:
        Wishlist.objects.create(user=request.user, product=product)

    return redirect('shop:product_detail', id=product.id, slug=product.slug)

from decimal import Decimal

from decimal import Decimal

def apply_voucher(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        cart = request.session.get('cart', {})

        # --- Áp dụng cho cart bình thường ---
        total_price = sum(Decimal(str(item.get('price', 0))) * int(item.get('quantity', 0)) for item in cart.values())

        if code == 'GIAM10':
            discount = total_price * Decimal('0.1')  # 10%
        elif code == 'GIAM50K':
            discount = Decimal('50000')  # 50k VND
        else:
            discount = Decimal('0')

        for key, item in cart.items():
            price = Decimal(str(item.get('price', 0)))
            qty = int(item.get('quantity', 1))
            item_discount = (price * qty / total_price * discount) if total_price > 0 else Decimal('0')
            discounted_price = (price - (item_discount / qty)).quantize(Decimal('0.01'))
            item['discounted_price'] = float(discounted_price)
            cart[key] = item

        request.session['cart'] = cart

        # --- 🔹 Áp dụng cho mua ngay ---
        buy_now_item = request.session.get('buy_now_item')
        if buy_now_item:
            price = Decimal(str(buy_now_item.get('price', 0)))
            if code == 'GIAM10':
                buy_now_item['discounted_price'] = float((price - price * Decimal('0.1')).quantize(Decimal('0.01')))
            elif code == 'GIAM50K':
                buy_now_item['discounted_price'] = float((price - Decimal('50000')).quantize(Decimal('0.01')))
            request.session['buy_now_item'] = buy_now_item

        request.session['voucher'] = code
        request.session.modified = True

    return redirect('shop:cart_detail')
