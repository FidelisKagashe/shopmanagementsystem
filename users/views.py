from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.views import LoginView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import CustomUserCreationForm
from datetime import timedelta
from io import BytesIO
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from .models import *  # Import the Profile model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, ListItem, ListFlowable

#Start matangazo printing process
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from products.models import *


@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home') 

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@method_decorator(never_cache, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    
    # Define maximum failed attempts and lockout time
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_TIME = 900  # 15 minutes (in seconds)

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the home page
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        lockout_info = cache.get(f"{username}_lockout")

        # Check if the user is still locked out
        if lockout_info:
            lockout_time, failed_attempts = lockout_info
            if timezone.now() < lockout_time:
                # Still locked out, deny login
                remaining_time = (lockout_time - timezone.now()).seconds // 60
                messages.error(self.request, f"Your account is locked. Try again in {remaining_time} minutes.")
                return self.form_invalid(form)  # Show the lockout message without allowing login

        # Proceed with login if not locked out
        user = form.get_user()
        login(self.request, user)

        # Reset failed attempts on successful login
        cache.delete(f"{username}_lockout")

        messages.success(self.request, f"Logged in successfully as {user.first_name} {user.last_name}")
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.cleaned_data.get('username')
        lockout_info = cache.get(f"{username}_lockout")

        # Check if lockout is already active
        if lockout_info:
            lockout_time, failed_attempts = lockout_info
            if timezone.now() < lockout_time:
                # User is locked out
                remaining_time = (lockout_time - timezone.now()).seconds // 60
                messages.error(self.request, f"Your account is locked. Try again in {remaining_time} minutes.")
                return self.render_to_response(self.get_context_data(form=form))  # Deny login attempt

        # Increment failed attempts count
        failed_attempts = cache.get(f"{username}_attempts", 0) + 1
        cache.set(f"{username}_attempts", failed_attempts, timeout=self.LOCKOUT_TIME)

        if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            # Lock the account by setting a lockout time in the cache
            lockout_time = timezone.now() + timedelta(seconds=self.LOCKOUT_TIME)
            cache.set(f"{username}_lockout", (lockout_time, failed_attempts), timeout=self.LOCKOUT_TIME)
            messages.error(self.request, f"Too many failed attempts. Your account is locked for 15 minutes.")
            return redirect('lockout')

        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def lockout_view(request):
    return render(request, 'users/lockout.html', context={
        'message': "You have been temporarily locked out due to too many failed login attempts. However, you can still browse the website as a guest. Please wait 15 minutes before trying to log in again. Thank you for your patience!"
    })

def get_cart_item_count(user):
    """Returns the total number of items in the user's cart."""
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        return sum(item.quantity for item in cart_items)
    return 0

def About(request):
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories':categories,
        'current_tab':'about',
        'cart_item_count':cart_item_count,
        }
    return render(request, 'users/about.html', context)

def Contact(request):
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories':categories,
        'current_tab':'contact',
        'cart_item_count':cart_item_count,
        }
    return render(request, 'users/contact.html', context)

def Faq(request):
    categories = Category.objects.all()
    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories':categories,
        'current_tab':'faq',
        'cart_item_count':cart_item_count,
        }
    return render(request, 'users/faq.html', context)

def Shop(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories':categories,
        'current_tab':'shop',
        'products':products,
        'cart_item_count':cart_item_count,
        }
    return render(request, 'users/shop.html', context)

# def Landing(request):
#     categories = Category.objects.all()
#     cart_item_count = get_cart_item_count(request.user)
#     context = {
#         'categories':categories,
#         'current_tab':'landing',
#         'cart_item_count':cart_item_count,
#         }
#     return render(request, 'users/landing.html', context)
