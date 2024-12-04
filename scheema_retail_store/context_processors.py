from .models import Cart

def cart_total_items(request):
    total_items = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart and cart.items.exists():
            total_items = sum(item.quantity for item in cart.items.all())
    else:
        session_cart = request.session.get('cart', {})
        if isinstance(session_cart, dict):
            total_items = sum(item.get('quantity', 0) for item in session_cart.values())

    return {'total_items_in_cart': total_items}

