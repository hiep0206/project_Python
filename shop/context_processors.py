def cart(request):
    cart_session = request.session.get('cart', {})
    
    # Tính tổng số lượng thực tế của tất cả các item
    # Tránh việc chỉ đếm số loại mặt hàng (len(cart))
    total_items = sum(item.get('quantity', 0) for item in cart_session.values())
    
    return {
        'cart_count': total_items # Đảm bảo tên này khớp với {{ cart_count }} trong base.html
    }