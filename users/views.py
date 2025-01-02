from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.views import LoginView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
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

        messages.success(self.request, f"Logged in successfully as {user.username}")
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
    """Displays the About page with top-level categories and their latest products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    category_products = {}
    for category in categories:
        # Fetch latest 4 products for each category's subcategories
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')[:4]
        category_products[category.id] = products

    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories': categories,
        'category_products': category_products,
        'current_tab': 'about',
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/about.html', context)


def Contact(request):
    """Displays the Contact page with top-level categories and their latest products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    category_products = {}
    for category in categories:
        # Fetch latest 4 products for each category's subcategories
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')[:4]
        category_products[category.id] = products

    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories': categories,
        'category_products': category_products,
        'current_tab': 'contact',
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/contact.html', context)


def Faq(request):
    """Displays the FAQ page with top-level categories and their latest products."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    category_products = {}
    for category in categories:
        # Fetch latest 4 products for each category's subcategories
        products = Product.objects.filter(category__in=category.subcategories.all()).order_by('-created_at')[:4]
        category_products[category.id] = products

    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories': categories,
        'category_products': category_products,
        'current_tab': 'faq',
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/faq.html', context)


def Shop(request):
    """Displays the Shop page with all products and categories."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    products = Product.objects.order_by('-created_at')[:20]  # Optionally fetch the latest 20 products
    cart_item_count = get_cart_item_count(request.user)
    context = {
        'categories': categories,
        'products': products,
        'current_tab': 'shop',
        'cart_item_count': cart_item_count,
    }
    return render(request, 'users/shop.html', context)

from django.shortcuts import render
from django.core.mail import send_mail
from django.core.cache import cache
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils.crypto import get_random_string
import logging
from .forms import EmailForm

# Initialize logger
logger = logging.getLogger(__name__)

def register_email(request):
    """Handle email registration and send a secure registration link."""
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            if User.objects.filter(email=email).exists():
                return render(request, 'users/email_taken.html', {
                    'error_message': "This email address is already registered. Please try another one or log in."
                })
            
            # Generate a secure token for the registration link
            token = get_random_string(32)
            cache_key = f"registration_token_{token}"
            cache_timeout = 3600  # 1 hour in seconds

            # Store email and token securely in cache
            cache.set(cache_key, email, timeout=cache_timeout)

            # Build the secure registration completion link
            site_domain = get_current_site(request).domain
            registration_link = f"{request.scheme}://{site_domain}{reverse('register_complete')}?token={token}"

            # Attempt to send the email
            try:
                send_mail(
                    subject="Complete Your Registration",
                    message=(
                        f"Click the link below to complete your registration:\n\n"
                        f"{registration_link}\n\n"
                        f"This link will expire in 1 hour."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                logger.info(f"Registration email sent to {email}")
                return render(request, 'users/email_sent.html')  # Redirect to a confirmation page
            except Exception as e:
                logger.error(f"Failed to send registration email to {email}: {str(e)}")
                return render(request, 'users/register.html', {
                    'form': form,
                    'error_message': "An error occurred while sending the email. Please try again later."
                })
        else:
            # Redisplay the form with validation errors
            return render(request, 'users/register.html', {
                'form': form,
                'error_message': "Invalid email address. Please try again."
            })

    else:
        form = EmailForm()

    return render(request, 'users/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from users.models import UserProfile
from users.forms import RegistrationForm

from django.core.cache import cache
from django.http import HttpResponse, Http404
from .models import UserProfile
from .forms import RegistrationForm

def register_complete(request):
    """Complete the registration process."""
    token = request.GET.get('token')  # Retrieve the token from the query parameters

    if not token:
        return HttpResponse("Invalid or expired registration link. Please start the registration process again.")

    # Retrieve email from the cache
    cache_key = f"registration_token_{token}"
    email = cache.get(cache_key)

    if not email:
        return HttpResponse("Invalid or expired registration link. Please start the registration process again.")

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create a new user with the provided data
                user = form.save(commit=False)
                user.email = email  # Set email retrieved from the cache
                user.save()

                # Check if a UserProfile already exists
                user_profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'phone_number': form.cleaned_data['phone_number']}
                )

                if not created:
                    # Update existing profile fields if needed
                    user_profile.phone_number = form.cleaned_data['phone_number']
                    user_profile.save()

                # Clear the token from the cache after successful registration
                cache.delete(cache_key)

                # Redirect to the login page or a success page
                return redirect('login')  # Replace 'login' with the actual login URL name

            except Exception as e:
                # Log the error for debugging and provide user feedback
                print(f"Error during registration: {e}")
                return HttpResponse("An unexpected error occurred. Please try again later.")

        else:
            # Re-render the form with errors
            return render(request, 'users/register2.html', {'form': form})
    else:
        # Pre-fill the form with the email from the cache
        form = RegistrationForm(initial={'email': email})

    return render(request, 'users/register2.html', {'form': form})





# import random
# from django.core.mail import send_mail
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth.models import User
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse
# from django.shortcuts import render, redirect
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
# from django.contrib.auth.forms import SetPasswordForm
# from django.utils import timezone
# from datetime import timedelta
# from django.conf import settings
# from django.contrib import messages

# # Model to store the reset code with an expiration time
# from .models import PasswordResetCode


# class CustomPasswordResetView(PasswordResetView):
#     """View to send password reset email with a 6-digit code."""
#     template_name = 'users/password_reset_form.html'
    
#     def form_valid(self, form):
#         email = form.cleaned_data['email']
#         user = User.objects.filter(email=email).first()
        
#         if user:
#             # Generate a six-digit code
#             reset_code = str(random.randint(100000, 999999))
#             # Store the reset code in the database with an expiration time (10 minutes)
#             reset_code_entry = PasswordResetCode.objects.create(
#                 user=user, 
#                 reset_code=reset_code,
#                 created_at=timezone.now()
#             )

#             # Send the reset code via email
#             subject = 'Your Password Reset Code'
#             message = f'Your password reset code is {reset_code}. This code is valid for 10 minutes.'
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

#             # Generate uidb64 and token for the password reset URL
#             uidb64 = urlsafe_base64_encode(str(user.id).encode())
#             token = default_token_generator.make_token(user)

#             # Redirect to the password reset confirm page
#             return redirect('password_reset_confirm', uidb64=uidb64, token=token)
#         else:
#             # Handle the case where no user is found with the provided email
#             form.add_error('email', 'No user found with this email address.')
#             return self.form_invalid(form)

# class CustomPasswordResetDoneView(PasswordResetDoneView):
#     """View to notify the user that the reset code has been sent."""
#     template_name = 'users/password_reset_done.html'

#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)

#         # Retrieve the email from the form data (POST request)
#         email = self.request.POST.get('email')  # This is where the email comes from
#         user = User.objects.filter(email=email).first()  # Get the user based on email

#         if user:
#             # Generate uidb64 and token for the password reset URL
#             uidb64 = urlsafe_base64_encode(str(user.id).encode())
#             token = default_token_generator.make_token(user)

#             context['uidb64'] = uidb64
#             context['token'] = token
        
#         return context

import logging
import secrets
from uuid import uuid4
from datetime import timedelta
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from .models import PasswordResetCode, User

logger = logging.getLogger(__name__)

# Utility function to generate a secure reset code
def generate_reset_code():
    return ''.join(secrets.choice('0123456789') for _ in range(6))

# Utility function to send password reset email
def send_reset_email(email, reset_code):
    subject = "Your Password Reset Code"
    message = f"Your password reset code is {reset_code}. This code is valid for 10 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# Password reset request view
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            reset_code = generate_reset_code()
            uidb64 = urlsafe_base64_encode(str(user.id).encode())
            token = default_token_generator.make_token(user)
            expiration_time = timezone.now() + timedelta(minutes=10)
            request_token = uuid4()

            # Save reset code and metadata to the database
            PasswordResetCode.objects.create(
                user=user,
                reset_code=reset_code,
                uidb64=uidb64,
                token=token,
                expires_at=expiration_time,
                request_token=request_token
            )

            # Send the reset code via email
            send_reset_email(email, reset_code)

            return redirect('password_reset_confirm', uidb64=uidb64, token=token, request_token=request_token)

        # If the user is not found, display an error message
        messages.error(request, 'The email address is not registered.')
        return redirect('password_reset')  # Redirect back to the reset form for better UX

    return render(request, 'users/password_reset_form.html')

# Password reset confirmation view
def password_reset_confirm(request, uidb64, token, request_token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.error("Invalid user ID in reset link.")
        return render(request, 'users/password_reset_confirm.html', {'error_message': 'Invalid reset link.'})

    reset_code_entry = PasswordResetCode.objects.filter(user=user, request_token=request_token).last()

    if not reset_code_entry or not default_token_generator.check_token(user, token):
        return render(request, 'users/password_reset_confirm.html', {'error_message': 'Invalid or expired reset token.'})

    if timezone.now() > reset_code_entry.expires_at:
        return render(request, 'users/password_reset_confirm.html', {'error_message': 'The reset code has expired.'})
    
    # Check the number of failed attempts and the timestamp in the session
    if 'failed_attempts' not in request.session or 'first_failed_at' not in request.session:
        request.session['failed_attempts'] = 0
        request.session['first_failed_at'] = timezone.now().timestamp()  # Store current time when first failed attempt occurs

    # If 30 minutes (1800 seconds) have passed since the first failure, reset the attempts
    if timezone.now().timestamp() - request.session['first_failed_at'] > 600:  # 300 seconds = 10 minutes
        request.session['failed_attempts'] = 0
        request.session['first_failed_at'] = timezone.now().timestamp()  # Reset the timer

    # Redirect to home page after 5 failed attempts
    if request.session['failed_attempts'] >= 3:
        messages.error(request, 'You have entered incorrect reset codes 3 times. Please try again later.')
        return redirect('home')  # Replace 'home' with your actual home page URL name

    if request.method == 'POST':
        reset_code = ''.join([request.POST.get(f'reset_code_{i}') for i in range(1, 7)])
        if reset_code != reset_code_entry.reset_code:
            # Increment failed attempts if the code is incorrect
            request.session['failed_attempts'] += 1
            return render(request, 'users/password_reset_confirm.html', {'error_message': 'Invalid reset code.'})

        # Reset the failed attempts counter on successful code entry
        request.session['failed_attempts'] = 0
        return redirect('password_reset_form', uidb64=uidb64, token=token)

    return render(request, 'users/password_reset_confirm.html', {
        'uidb64': uidb64,
        'token': token,
        'request_token': request_token,
        'user': user,
    })

# Resend reset code view
def resend_reset_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            reset_code = generate_reset_code()
            PasswordResetCode.objects.update_or_create(
                user=user,
                defaults={'reset_code': reset_code, 'created_at': timezone.now()}
            )
            send_reset_email(email, reset_code)
            return redirect('password_reset_request')

        return render(request, 'users/password_reset_resend.html', {'error_message': 'No user found with this email address.'})

    return render(request, 'users/password_reset_resend.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages

def password_reset_form(request, uidb64, token):
    try:
        # Decode the user ID from the base64 string
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                # Save the new password
                form.save()
                messages.success(request, "Your password has been reset successfully!")
                return redirect('login')  # Redirect to login page after successful password reset
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset_form2.html', {'form': form})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('password_reset')  # Redirect to the password reset request page
