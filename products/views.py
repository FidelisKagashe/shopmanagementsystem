from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Category

def get_cart_item_count(user):
    """Returns the total number of items in the user's cart."""
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        return sum(item.quantity for item in cart_items)
    return 0

def Home(request):
    """Displays the homepage with categories and their latest four products."""
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)

    # Pre-process data in the view to only include the latest four products for each category
    category_products = {}
    for category in categories:
        # Get the latest four products for each category
        products = category.products.all().order_by('-created_at')[:4]  # Assuming 'created_at' is the field to order by
        category_products[category.id] = products

    context = {
        'current_tab':'home',
        'categories': categories,
        'category_products': category_products,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/landing.html', context)
    
def product_list(request):
    """Displays the list of all products."""
    categories = Category.objects.all()
    products = Product.objects.all()
    cart_item_count = get_cart_item_count(request.user)

    context = {
        'products': products,
        'current_tab':'shop',
        'categories': categories,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    """Displays the details of a single product."""
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'current_tab':'shop',
        'categories': categories,
        'cart_item_count': cart_item_count,
    })

def products_by_category(request, category_name):
    """Displays products filtered by category."""
    category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)

    return render(request, 'products/product_list.html', {
        'products': products,
        'current_tab':'shop',
        'categories': categories,
        'category_name': category_name,
        'cart_item_count': cart_item_count,
    })

@login_required
def add_to_cart(request, product_id):
    """Adds a product to the user's cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))  # Use POST to get quantity

    if product.stock >= quantity:
        # If the item already exists in the cart, update its quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, f"{product.name} has been added to your cart!")
    else:
        messages.error(request, f"Not enough stock for {product.name}.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirect back to the referring page

@login_required
def view_cart(request):
    """Displays the cart with all items and total sum."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_item_count = sum(item.quantity for item in cart_items)
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    categories = Category.objects.all()

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum,
        'current_tab':'cart',
        'cart_item_count': cart_item_count,
        'cart': cart
    })

@login_required
def remove_from_cart(request, pk):
    """Removes an item from the cart."""
    cart_item = get_object_or_404(CartItem, pk=pk)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')

@login_required
def checkout(request):
    """Displays the checkout page with cart items and total price."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    categories = Category.objects.all()

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum
    })

@login_required
def process_payment(request):
    """Processes the payment and updates stock and order status."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Deduct stock and mark the cart as ordered
    cart.update_stock_after_checkout()  # This method would update product stock after checkout
    cart.is_ordered = True  # Mark the cart as ordered
    cart.save()

    messages.success(request, 'Payment processed successfully! Your order is confirmed.')
    return redirect('view_cart')
