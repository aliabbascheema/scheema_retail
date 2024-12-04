import contextlib
from django.contrib import messages
from django.dispatch import receiver
from django.shortcuts import redirect, render, get_object_or_404
from .models import Cart, CartItem, Category, Order, OrderItem, Product, UserProfile
from .models import Product
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.db.models.signals import post_save
from django.core.files.storage import default_storage

class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.user.is_authenticated:
            session_cart = self.request.session.get('cart', {})
            if session_cart:
                cart, created = Cart.objects.get_or_create(
                    user=self.request.user)

                for product_id, item in session_cart.items():
                    product = get_object_or_404(Product, id=product_id)
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=product)

                    if not created:
                        cart_item.quantity += item['quantity']
                    else:
                        cart_item.quantity = item['quantity']
                    cart_item.save()

                del self.request.session['cart']

                messages.success(
                    self.request, 'Cart items migrated to your account')

        return response


def register(request):  # sourcery skip: extract-method
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(
            username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'stores/register.html')

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
    instance.profile.save()
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

def update_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = request.user.profile
    if request.method == 'POST':
        return _update_profile_actions(request, profile)
    return render(request, 'stores/settings.html', {'profile': profile})


def _update_profile_actions(request, profile):
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    description = request.POST.get('description', '').strip()
    job_title = request.POST.get('job_title', '').strip()
    social_links = {
        'linkedin': request.POST.get('linkedin', '').strip(),
        'twitter': request.POST.get('twitter', '').strip(),
        'github': request.POST.get('github', '').strip(),
    }

    profile_image = request.FILES.get('profile_image')
    if profile_image:
        if profile.profile_image:
            default_storage.delete(profile.profile_image.path)  # Delete old image
        profile.profile_image = profile_image

    user = request.user
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('update_profile')
        user.email = email

    user.save()
    profile.description = description
    profile.job_title = job_title
    profile.social_links = social_links
    profile.save()

    messages.success(request, 'Your profile has been updated successfully!')
    return redirect('dashboard')


def home(request):
    products = Product.objects.all()
    return render(request, 'stores/home.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    reviews = product.reviews.all()
    total_reviews = reviews.count()
    average_rating = 0
    if total_reviews > 0:
        average_rating = sum([review.rating for review in reviews]) / total_reviews

    features = [feature.strip()
                for feature in product.features.split('\n') if feature.strip()]

    total_qty_in_cart = 0

    if request.user.is_authenticated:
        with contextlib.suppress(Cart.DoesNotExist):
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.filter(
                cart=cart, product=product).first()
            if cart_item:
                total_qty_in_cart = cart_item.quantity
    else:
        cart = request.session.get('cart', {})
        if str(product.id) in cart:
            total_qty_in_cart = cart[str(product.id)]['quantity']

    return render(request, 'stores/product_detail.html', {
        'product': product,
        'features': features,
        'total_qty_in_cart': total_qty_in_cart,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'reviews': reviews,
        'range_5': range(1, 6)
    })


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'stores/category_products.html', {'category': category, 'products': products})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()

        messages.success(request, f'{product.title} added to cart')

    else:
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {'quantity': 1, 'title': product.title}

        request.session['cart'] = cart

        messages.success(request, f'{product.title} added to cart (session)')
    referer = request.META.get('HTTP_REFERER', '')
    if referer and f'/product/{product.slug}/' in referer:
        return redirect(f'/product/{product.slug}/')
    else:
        return redirect('home')


def remove_from_cart(request, cart_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)

        cart_item = CartItem.objects.filter(
            cart=cart, product__id=cart_id).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(
                    request, f'{cart_item.product.title} quantity decreased by 1.')
            else:
                cart_item.delete()
                messages.success(
                    request, f'{cart_item.product.title} removed from cart.')
        else:
            messages.error(request, 'Item not found in cart.')

    else:
        cart = request.session.get('cart', {})

        if str(cart_id) in cart:
            product_name = cart[str(cart_id)]["title"]

            if cart[str(cart_id)]['quantity'] > 1:
                cart[str(cart_id)]['quantity'] -= 1
                request.session['cart'] = cart
                messages.success(
                    request, f'{product_name} quantity decreased by 1.')
            else:
                del cart[str(cart_id)]
                request.session['cart'] = cart
                messages.success(request, f'{product_name} removed from cart.')
        else:
            messages.error(request, 'Item not found in cart.')

    return redirect('view_cart')


def view_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        cart_items_with_details = [
            {
                'product': {
                    'id': item.product.id,
                    'slug': item.product.slug,
                    'title': item.product.title,
                    'description': item.product.description,
                    'price': item.product.price,
                    'image': item.product.image,
                    'category': item.product.category.name if item.product.category else None,
                    'stock': item.product.stock
                },
                'quantity': item.quantity,
                'subtotal': item.quantity * item.product.price
            }
            for item in cart_items
        ]
    else:
        cart = request.session.get('cart', {})
        cart_items_with_details = [
            {
                'product': {
                    'id': Product.objects.get(id=product_id).id,
                    'slug': Product.objects.get(id=product_id).slug,
                    'title': item['title'],
                    'description': Product.objects.get(id=product_id).description,
                    'price': Product.objects.get(id=product_id).price,
                    'image': Product.objects.get(id=product_id).image,
                    'category': Product.objects.get(id=product_id).category.name if Product.objects.get(id=product_id).category else None,
                    'stock': Product.objects.get(id=product_id).stock
                },
                'quantity': item['quantity'],
                'subtotal': item['quantity'] * Product.objects.get(id=product_id).price
            }
            for product_id, item in cart.items()
        ]

    total_items_in_cart = get_cart_total_items(request)
    total_cost = sum(item['subtotal'] for item in cart_items_with_details)

    return render(request, 'stores/cart.html', {
        'cart_items': cart_items_with_details,
        'total_items_in_cart': total_items_in_cart,
        'total_cost': total_cost
    })


def get_cart_total_items(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        return sum([item.quantity for item in cart.items.all()])
    else:
        cart = request.session.get('cart', {})
        return sum(item['quantity'] for item in cart.values())


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'stores/search.html', {'products': products, 'query': query})

def place_order(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()

    if not cart or not cart.items.exists():
        return redirect('view_cart')

    total_cost = sum(item.total_price for item in cart.items.all())

    if total_cost > 0:
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_price=total_cost
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                image=item.product.image if hasattr(
                    item.product, 'image') else None
            )

        cart.items.all().delete()

        return redirect('dashboard')

    return redirect('view_cart')


def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'stores/dashboard.html', {'orders': orders})