from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Category
from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def get_cart_item_count(user):
    """Returns the total number of items in the user's cart."""
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        return sum(item.quantity for item in cart_items)
    return 0

def Home(request):
    """Displays the homepage with top-level categories and their latest products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    cart_item_count = get_cart_item_count(request.user)

    category_products = {}
    for category in categories:
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')[:4]
        category_products[category.id] = products

    context = {
        'current_tab': 'home',
        'categories': categories,
        'category_products': category_products,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/landing.html', context)


def product_list(request):
    """Displays the list of all products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    products = Product.objects.all()
    cart_item_count = get_cart_item_count(request.user)

    context = {
        'products': products,
        'current_tab': 'shop',
        'categories': categories,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    """Displays the details of a single product."""
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.filter(parent__isnull=True)
    cart_item_count = get_cart_item_count(request.user)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'current_tab': 'shop',
        'categories': categories,
        'cart_item_count': cart_item_count,
    })

def products_by_subcategory(request, subcategory_name):
    """Displays products filtered by a subcategory."""
    subcategory = get_object_or_404(Category, name=subcategory_name)
    products = Product.objects.filter(category=subcategory)
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    cart_item_count = get_cart_item_count(request.user)

    return render(request, 'products/product_list.html', {
        'products': products,
        'current_tab': 'shop',
        'categories': categories,
        'subcategory_name': subcategory_name,
        'cart_item_count': cart_item_count,
    })


@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the user's cart or updates the quantity if already in the cart.
    """
    # Get or create the cart for the current user
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # Retrieve the product
    product = get_object_or_404(Product, id=product_id)
    
    # Validate quantity from request
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'home'))
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity specified.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'home'))

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Validate stock availability
    if product.stock >= (cart_item.quantity + quantity if not created else quantity):
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, f"{product.name} has been added to your cart! (Quantity: {cart_item.quantity})")
    else:
        messages.error(request, f"Only {product.stock} units of {product.name} are available.")

    # Redirect to the referring page or home if not available
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def view_cart(request):
    """Displays the cart with all items and total sum."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_item_count = sum(item.quantity for item in cart_items)
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    categories = Category.objects.filter(parent__isnull=True)

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum,
        'current_tab': 'cart',
        'cart_item_count': cart_item_count,
        'cart': cart
    })


@login_required
def remove_from_cart(request, pk):
    """Removes an item from the logged-in user's cart."""
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    
    # Delete the cart item
    cart_item.delete()
    messages.success(request, f'Item "{cart_item.product.name}" removed from cart.')
    
    return redirect('view_cart')

@login_required
def checkout(request):
    """Displays the checkout page with cart items and total price."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    categories = Category.objects.filter(parent__isnull=True)
    cart_item_count = sum(item.quantity for item in cart_items)

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum,
        'cart_item_count':cart_item_count,
    })


from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

@login_required
def place_order(request):
    """Handles the Place Order process and sends emails with product images embedded."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect('shop')

    # Calculate the total price for each product and the grand total
    grand_total = 0
    calculated_items = []
    for item in cart_items:
        total_price = item.product.price * item.quantity
        grand_total += total_price
        calculated_items.append({
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.product.price,
            "total_price": total_price,
            "image_name": item.product.image.name,
            "image_url": item.product.image.url,
        })

    # Prepare the HTML message body with cart data for the customer
    html_content = render_to_string(
        'products/order_email_template.html',
        {
            "calculated_items": calculated_items,  # Pass the calculated items
            "user": request.user,
            "grand_total": grand_total,  # Pass the grand total to the email template
        }
    )

    # Create the email with embedded images for the customer
    email = EmailMultiAlternatives(
        subject="Order Confirmation",
        body="Your order has been successfully placed.",
        from_email="fideliskagashe@gmail.com",
        to=[request.user.email],
    )
    email.attach_alternative(html_content, "text/html")

    # Embed product images as MIME images
    for item in calculated_items:
        with open(item["image_url"][1:], 'rb') as img_file:  # Adjust to strip leading slash from image URL
            email.attach(
                item["image_name"],
                img_file.read(),
                'image/jpeg'
            )
            html_content = html_content.replace(
                item["image_url"],
                f'cid:{item["image_name"]}'
            )
    email.attach_alternative(html_content, "text/html")

    # Send the email to the customer
    email.send()

    # Notify the superuser about the order
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        admin_emails = [user.email for user in superusers if user.email]
        if admin_emails:
            admin_subject = f"New Order from {request.user.username}"
            admin_message = render_to_string(
                'products/admin_order_notification.html',
                {
                    "user": request.user,
                    "calculated_items": calculated_items,
                    "grand_total": grand_total,
                }
            )
            admin_email_message = EmailMessage(
                subject=admin_subject,
                body=admin_message,
                from_email="fideliskagashe@gmail.com",
                to=admin_emails,
            )
            admin_email_message.content_subtype = "html"
            admin_email_message.send()

    # Clear the cart after sending the order confirmation
    cart_items.delete()

    # Render the confirmation page
    return render(request, 'products/order_confirmation.html',
                   {"grand_total": grand_total,
                    "calculated_items": calculated_items,
                    })

@login_required
def process_payment(request):
    """Processes the payment and updates stock and order status."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    cart.update_stock_after_checkout()
    cart.is_ordered = True
    cart.save()

    messages.success(request, 'Payment processed successfully! Your order is confirmed.')
    return redirect('view_cart')

@login_required
def update_cart(request, product_id):
    """Updates the quantity of a product in the cart."""
    if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
        else:
            cart_item = get_object_or_404(CartItem, cart=cart, product=product)
            if product.stock >= new_quantity:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f"Updated quantity for {product.name} to {new_quantity}.")
            else:
                messages.error(request, f"Not enough stock for {product.name}.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'view_cart'))