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
        # Retrieve the cart for the user
        cart = Cart.objects.filter(user=user).first()
        
        # If the cart exists, get the total item count
        if cart:
            # Use aggregate to sum the quantities in the cart more efficiently
            return cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    return 0


def Home(request):
    """Displays the homepage with top-level categories and their latest products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    cart_item_count = get_cart_item_count(request.user)

    category_products = {}
    for category in categories:
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')
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


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Product

@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the user's cart or updates the quantity if already in the cart.
    Returns the updated cart item count and total price in JSON for AJAX handling.
    """
    # Get or create the cart for the current user
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Retrieve the product
    product = get_object_or_404(Product, id=product_id)

    # Validate quantity from request
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return JsonResponse({"error": "Quantity must be at least 1."}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid quantity specified."}, status=400)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Validate stock availability
    if product.stock >= cart_item.quantity + quantity:
        if not created:
            cart_item.quantity += quantity  # Update the quantity for existing item
        else:
            cart_item.quantity = quantity  # Set the quantity for a new item
        cart_item.save()

        # Get updated cart item count and total
        cart_item_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        cart_total = cart.total_price()

        # Return updated information
        return JsonResponse({
            "message": f"{product.name} has been added to your cart! (Quantity: {cart_item.quantity})",
            "cart_item_count": cart_item_count,
            "cart_total": f"Tsh {cart_total:.2f}",
        })
    else:
        return JsonResponse({"error": f"Only {product.stock} units of {product.name} are available."}, status=400)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Cart, CartItem, Category


def view_cart(request):
     # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('register_email')  # Redirect to the register_email page if not authenticated
    
    """Displays the cart with all items and total sum."""
    # Get or create the cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Retrieve cart items
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate total item count (sum of quantities)
    cart_item_count = cart_items.aggregate(total=Sum('quantity'))['total'] or 0

    # Calculate the total sum for the cart
    total_sum = cart.total_price()

    # Fetch categories (assuming a parent-child relationship)
    categories = Category.objects.filter(parent__isnull=True)

    # Return the rendered cart view
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum,
        'current_tab': 'cart',
        'cart_item_count': cart_item_count,
        'cart': cart
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem

@login_required
def remove_from_cart(request, pk):
    """Removes an item from the logged-in user's cart."""
    try:
        # Get the CartItem object for the given pk and user's cart
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)

        # Delete the cart item
        cart_item.delete()
        
        # Send success message
        messages.success(request, f'Item "{cart_item.product.name}" removed from cart.')

    except CartItem.DoesNotExist:
        # In case the cart item does not exist, send an error message
        messages.error(request, 'This item could not be found in your cart.')

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


from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from users.models import UserProfile
import logging


# Set up logging
logger = logging.getLogger(__name__)

@login_required
def place_order(request):
    """Handles the Place Order process and sends emails with product images embedded."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    category_products = {}
    for category in categories:
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')
        category_products[category.id] = products
        
    if not cart_items.exists():
        return redirect('shop')
    
    if request.method == 'POST':
        city = request.POST.get('city')
        address = request.POST.get('address')

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
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        customer_phone = user_profile.phone_number
    except UserProfile.DoesNotExist:
        customer_phone = "Phone number not provided"

    # Prepare the HTML message body with cart data for the customer
    html_content = render_to_string(
        'products/order_email_template.html',
        {
            "calculated_items": calculated_items,  # Pass the calculated items
            "user": request.user,
            "grand_total": grand_total,
            "customer_phone": customer_phone,
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
                f'cid:{item["image_name"]}'  # Use CID to embed image in email
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

            # Get the user's phone number
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                customer_phone = user_profile.phone_number
            except UserProfile.DoesNotExist:
                customer_phone = "Phone number not provided"

            # Include the customer's phone number in the admin email
            admin_message = render_to_string(
                'products/admin_order_notification.html',
                {
                    "user": request.user,
                    "calculated_items": calculated_items,
                    "grand_total": grand_total,
                    "customer_phone": customer_phone,  # Include phone number
                    "city": city,  # Include the city
                    "address": address,  # Include the address
                }
            )

            # Include product images in admin email
            admin_email_message = EmailMessage(
                subject=admin_subject,
                body=admin_message,
                from_email="fideliskagashe@gmail.com",
                to=admin_emails,
            )

            # Attach product images to the admin email
            for item in calculated_items:
                with open(item["image_url"][1:], 'rb') as img_file:
                    admin_email_message.attach(
                        item["image_name"],
                        img_file.read(),
                        'image/jpeg'
                    )
                    admin_message = admin_message.replace(
                        item["image_url"],
                        f'cid:{item["image_name"]}'  # Embed images in the email
                    )
            
            admin_email_message.content_subtype = "html"
            admin_email_message.send()

    # Clear the cart after sending the order confirmation
    cart_items.delete()

    # Render the confirmation page
    return render(request, 'products/order_confirmation.html',
                   {"grand_total": grand_total,
                    "calculated_items": calculated_items,
                    'categories': categories,
                    'category_products': category_products,
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