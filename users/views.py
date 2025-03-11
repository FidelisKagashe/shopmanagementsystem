from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from decimal import Decimal
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import json

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, inlineformset_factory
from django.views.generic import ListView
from django.utils import timezone
from django.db.models import Sum
from .models import SaleOrder, SaleOrderItem, Product

import logging
import secrets
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.forms import inlineformset_factory
from .models import SaleOrder, SaleOrderItem
from .forms import SaleOrderForm, SaleOrderItemForm, SaleOrderItemFormSet  # Ensure your formset is imported
from uuid import uuid4
from datetime import timedelta
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from .models import PasswordResetCode, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from .forms import CustomAuthenticationForm
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django import forms
from django.views.decorators.cache import never_cache
from django.forms import ModelForm, inlineformset_factory
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Sum
from django.utils import timezone
from .models import Product, Supplier, Customer, PurchaseOrder, SaleOrder, Invoice, SaleReturn, Promotion, SaleOrderItem


# -------------------------------
# Dashboard (Home) View
# -------------------------------

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from .models import Product, Supplier, Customer, PurchaseOrder, SaleOrder, UserFinancialTransaction

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Product, Supplier, Customer, PurchaseOrder, SaleOrder, UserFinancialTransaction

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard summary counts
        context.update({
            'total_products': Product.objects.count(),
            'total_suppliers': Supplier.objects.count(),
            'total_customers': Customer.objects.count(),
            'total_purchase_orders': PurchaseOrder.objects.count(),
            'total_sale_orders': SaleOrder.objects.count(),
        })
        
        credit_entries = []
        debit_entries = []
        
        # Process Sale Orders (money received):
        # Only consider completed sale orders with a valid payment status.
        sale_orders = SaleOrder.objects.filter(status='Completed').exclude(payment_status='Unpaid')
        for order in sale_orders:
            cash_amount = order.total_amount if order.payment_status == 'Cash' else 0
            bank_amount = order.total_amount if order.payment_status == 'Bank' else 0
            credit_entries.append({
                'date': order.order_date,
                'description': f"Sale Order #{order.id} for {order.customer.name}",
                'transaction_type': 'CR',  # Credit: money received
                'cash': cash_amount,
                'bank': bank_amount,
                'discount': 0,  # Placeholder for discount adjustments if needed
            })
        
        # Process Purchase Orders (money paid):
        # Consider purchase orders that have reached a stage where payment is made.
        # You can adjust the filter (e.g., Delivered, Approved) as per your business rules.
        purchase_orders = PurchaseOrder.objects.filter(status__in=['Approved', 'Delivered'])
        for order in purchase_orders:
            cash_amount = order.total_amount if order.payment_method == 'Cash' else 0
            bank_amount = order.total_amount if order.payment_method == 'Bank' else 0
            debit_entries.append({
                'date': order.order_date,
                'description': f"Purchase Order #{order.id} from {order.supplier.name}",
                'transaction_type': 'DR',  # Debit: money paid out
                'cash': cash_amount,
                'bank': bank_amount,
                'discount': 0,  # Placeholder for discount adjustments if needed
            })
        
        # Process User Financial Transactions:
        # Only approved transactions are considered.
        transactions = UserFinancialTransaction.objects.filter(approved=True)
        for trans in transactions:
            entry = {
                'date': trans.date,
                'description': trans.description,
                'cash': trans.amount if trans.account == 'CASH' else 0,
                'bank': trans.amount if trans.account == 'BANK' else 0,
                'discount': 0,  # Placeholder for future discount logic if required
            }
            if trans.transaction_type == 'ADD':
                entry['transaction_type'] = 'CR'
                credit_entries.append(entry)
            elif trans.transaction_type == 'REMOVE':
                entry['transaction_type'] = 'DR'
                debit_entries.append(entry)
        
        # Combine credit and debit entries
        all_entries = credit_entries + debit_entries
        all_entries.sort(key=lambda x: x['date'])
        
        # Compute a running balance (starting from 0)
        running_balance = 0
        for entry in all_entries:
            if entry['transaction_type'] == 'CR':
                running_balance += entry['cash'] + entry['bank']
            else:  # 'DR'
                running_balance -= entry['cash'] + entry['bank']
            entry['balance'] = running_balance
        
        context['cashbook_entries'] = all_entries
        
        return context

# -------------------------------
# Product Views
# -------------------------------

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'unit_price', 'quantity_in_stock',
              'minimum_stock_level']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'unit_price', 'quantity_in_stock',
              'minimum_stock_level']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# -------------------------------
# Supplier Views
# -------------------------------

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    fields = ['name', 'contact_number', 'email', 'address']
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    fields = ['name', 'contact_number', 'email', 'address']
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

# -------------------------------
# Customer Views
# -------------------------------

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    fields = ['name', 'contact_number', 'email', 'address']
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add HTML required attribute to each field
        for field in self.fields:
            form.fields[field].widget.attrs.update({'required': 'required'})
        return form


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    fields = ['name', 'contact_number', 'email', 'address']
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add HTML required attribute to each field
        for field in self.fields:
            form.fields[field].widget.attrs.update({'required': 'required'})
        return form

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import PurchaseOrder

# -------------------------------
# Purchase Order Views
# -------------------------------

class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchase_orders/purchaseorder_list.html'
    context_object_name = 'purchase_orders'


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchase_orders/purchaseorder_detail.html'
    context_object_name = 'purchase_order'


class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    # Include the new payment_method field along with supplier, status, and total_amount
    fields = ['supplier', 'status', 'total_amount', 'payment_method']
    template_name = 'purchase_orders/purchaseorder_form.html'
    success_url = reverse_lazy('purchaseorder_list')


class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    # Include the new payment_method field in the update form as well
    fields = ['supplier', 'status', 'total_amount', 'payment_method']
    template_name = 'purchase_orders/purchaseorder_form.html'
    success_url = reverse_lazy('purchaseorder_list')


class PurchaseOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = 'purchase_orders/purchaseorder_confirm_delete.html'
    success_url = reverse_lazy('purchaseorder_list')



class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'

# -------------------------------
# Sale Return Views
# -------------------------------

class SaleReturnListView(LoginRequiredMixin, ListView):
    model = SaleReturn
    template_name = 'sale_returns/salereturn_list.html'
    context_object_name = 'sale_returns'

class SaleReturnCreateView(LoginRequiredMixin, CreateView):
    model = SaleReturn
    fields = ['sale_order_item', 'quantity', 'reason']
    template_name = 'sale_returns/salereturn_form.html'
    success_url = reverse_lazy('salereturn_list')

# -------------------------------
# Promotion Views
# -------------------------------

class PromotionListView(LoginRequiredMixin, ListView):
    model = Promotion
    template_name = 'promotions/promotion_list.html'
    context_object_name = 'promotions'

class PromotionCreateView(LoginRequiredMixin, CreateView):
    model = Promotion
    fields = ['name', 'discount_percentage', 'start_date', 'end_date']
    template_name = 'promotions/promotion_form.html'
    success_url = reverse_lazy('promotion_list')

class PromotionUpdateView(LoginRequiredMixin, UpdateView):
    model = Promotion
    fields = ['name', 'discount_percentage', 'start_date', 'end_date']
    template_name = 'promotions/promotion_form.html'
    success_url = reverse_lazy('promotion_list')

class PromotionDeleteView(LoginRequiredMixin, DeleteView):
    model = Promotion
    template_name = 'promotions/promotion_confirm_delete.html'
    success_url = reverse_lazy('promotion_list')


#AUTHENTICATION


@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


@method_decorator(never_cache, name='dispatch')
class CustomLoginView(FormView):
    template_name = 'Authentication/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')
    form_class = CustomAuthenticationForm

    # Define maximum failed attempts and lockout time
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # 5 minutes (in seconds)

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the dashboard page
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        lockout_info = cache.get(f"{email}_lockout")

        # Check if the user is still locked out
        if lockout_info:
            lockout_time, failed_attempts = lockout_info
            if timezone.now() < lockout_time:
                # Still locked out, deny login
                remaining_time = (lockout_time - timezone.now()).seconds // 60
                messages.error(self.request, f"Your account is locked. Try again in {remaining_time} minutes.")
                return self.form_invalid(form)  # Show the lockout message without allowing login

        # Proceed with login if not locked out
        username = form.cleaned_data.get('username')  # The username stored in cleaned_data
        password = form.cleaned_data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            # Reset failed attempts on successful login
            cache.delete(f"{email}_lockout")
            messages.success(self.request, f"Logged in successfully as {user.username}")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid email or password.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        email = form.cleaned_data.get('email')
        lockout_info = cache.get(f"{email}_lockout")

        # Check if lockout is already active
        if lockout_info:
            lockout_time, failed_attempts = lockout_info
            if timezone.now() < lockout_time:
                # User is locked out
                remaining_time = (lockout_time - timezone.now()).seconds // 60
                messages.error(self.request, f"Your account is locked. Try again in {remaining_time} minutes.")
                return self.render_to_response(self.get_context_data(form=form))  # Deny login attempt

        # Increment failed attempts count
        failed_attempts = cache.get(f"{email}_attempts", 0) + 1
        cache.set(f"{email}_attempts", failed_attempts, timeout=self.LOCKOUT_TIME)

        if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            # Lock the account by setting a lockout time in the cache
            lockout_time = timezone.now() + timedelta(seconds=self.LOCKOUT_TIME)
            cache.set(f"{email}_lockout", (lockout_time, failed_attempts), timeout=self.LOCKOUT_TIME)
            messages.error(self.request, f"Too many failed attempts. Your account is locked for 5 minutes.")
            return redirect('lockout')

        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)



def lockout_view(request):
    return render(request, 'Authentication/lockout.html', context={
        'message': "You have been temporarily locked out due to too many failed login attempts. However, you can still browse the website as a guest. Please wait 15 minutes before trying to log in again. Thank you for your patience!"
    })


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

    return render(request, 'Authentication/password_reset_form.html')

# Password reset confirmation view
def password_reset_confirm(request, uidb64, token, request_token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.error("Invalid user ID in reset link.")
        return render(request, 'Authentication/password_reset_confirm.html', {'error_message': 'Invalid reset link.'})

    reset_code_entry = PasswordResetCode.objects.filter(user=user, request_token=request_token).last()

    if not reset_code_entry or not default_token_generator.check_token(user, token):
        return render(request, 'Authentication/password_reset_confirm.html', {'error_message': 'Invalid or expired reset token.'})

    if timezone.now() > reset_code_entry.expires_at:
        return render(request, 'Authentication/password_reset_confirm.html', {'error_message': 'The reset code has expired.'})

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
        return redirect('login')  # Replace 'home' with your actual home page URL name

    if request.method == 'POST':
        reset_code = ''.join([request.POST.get(f'reset_code_{i}') for i in range(1, 7)])
        if reset_code != reset_code_entry.reset_code:
            # Increment failed attempts if the code is incorrect
            request.session['failed_attempts'] += 1
            return render(request, 'Authentication/password_reset_confirm.html', {'error_message': 'Invalid reset code.'})

        # Reset the failed attempts counter on successful code entry
        request.session['failed_attempts'] = 0
        return redirect('password_reset_form', uidb64=uidb64, token=token)

    return render(request, 'Authentication/password_reset_confirm.html', {
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

        return render(request, 'Authentication/password_reset_resend.html', {'error_message': 'No user found with this email address.'})

    return render(request, 'Authentication/password_reset_resend.html')

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
        return render(request, 'Authentication/password_reset_form2.html', {'form': form})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('password_reset')  # Redirect to the password reset request page
 
from decimal import Decimal
import json

from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SaleOrder, SaleOrderItem
from .models import SaleOrder, SaleOrderItem, Product


# Import your models. Adjust the import as per your project structure.

# -------------------------------------------------------------------------------
# SaleOrder Form (for the main sale order fields)
# -------------------------------------------------------------------------------
class SaleOrderForm(ModelForm):
    class Meta:
        model = SaleOrder
        fields = ['customer', 'status', 'payment_status']  # 'created_by' and 'total_amount' set automatically

    def __init__(self, *args, **kwargs):
        super(SaleOrderForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs.update({'class': 'form-control'})

# -------------------------------------------------------------------------------
# SaleOrderItem Form and FormSet
# -------------------------------------------------------------------------------

class SaleOrderItemForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = SaleOrderItem
        fields = ['product', 'quantity', 'sale_price', 'discount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for styling and functionality.
        self.fields['product'].widget.attrs.update({
            'class': 'product-select form-control',
            'required': 'required'
        })
        self.fields['quantity'].widget.attrs.update({
            'class': 'quantity-input form-control',
            'required': 'required'
        })
        self.fields['sale_price'].widget.attrs.update({
            'class': 'sale-price-input form-control',
            'readonly': 'readonly',
            'required': 'required'
        })
        self.fields['discount'].widget.attrs.update({
            'class': 'discount-input form-control'
        })
        
        # Set form field required flags.
        self.fields['product'].required = True
        self.fields['quantity'].required = True
        self.fields['sale_price'].required = True
        self.fields['discount'].required = False
        self.fields['discount'].initial = Decimal('0.00')

        # If editing an existing order item, prefill sale_price from the product.
        if self.instance.pk and self.instance.product:
            self.fields['sale_price'].initial = self.instance.product.unit_price

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        sale_price = cleaned_data.get('sale_price')
        discount = cleaned_data.get('discount') or Decimal('0.00')

        # Validate product.
        if not product:
            self.add_error('product', 'Please select a product.')
        
        # Validate quantity: required and greater than 0.
        if quantity is None:
            self.add_error('quantity', 'Quantity is required.')
        elif quantity <= 0:
            self.add_error('quantity', 'Quantity must be greater than 0.')

        # Validate sale price: required and greater than 0.
        if sale_price is None:
            self.add_error('sale_price', 'Sale price is required.')
        elif sale_price <= 0:
            self.add_error('sale_price', 'Sale price must be greater than 0.')

        # Validate discount: must be between 0 and 100.
        if discount < 0 or discount > 100:
            self.add_error('discount', 'Discount must be between 0 and 100.')

        return cleaned_data
        
SaleOrderItemFormSet = inlineformset_factory(
    SaleOrder,
    SaleOrderItem,
    form=SaleOrderItemForm,
    extra=1,
    can_delete=True
)

from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import SaleOrder

class SaleOrderListView(LoginRequiredMixin, ListView):
    model = SaleOrder
    template_name = 'sale_orders/saleorder_list.html'
    context_object_name = 'sale_orders'
    # Removed: paginate_by = 10

    def get_queryset(self):
        queryset = SaleOrder.objects.order_by('-order_date')
        order_date = self.request.GET.get('order_date', '')
        search = self.request.GET.get('search', '')
        if order_date:
            queryset = queryset.filter(order_date__date=order_date)
        if search:
            queryset = queryset.filter(
                Q(customer__name__icontains=search) |
                Q(created_by__username__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        todays_total = SaleOrder.objects.filter(order_date__date=today).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        context['todays_total'] = todays_total
        # Removed query_string from context as pagination is now client-side
        return context

# -------------------------------------------------------------------------------
# SaleOrder Detail View
# -------------------------------------------------------------------------------
class SaleOrderDetailView(LoginRequiredMixin, DetailView):
    model = SaleOrder
    template_name = 'sale_orders/saleorder_detail.html'
    context_object_name = 'sale_order'

# -------------------------------------------------------------------------------
# SaleOrder Create View with Inline Formset for Items
# -------------------------------------------------------------------------------
class SaleOrderCreateView(LoginRequiredMixin, CreateView):
    model = SaleOrder
    fields = ['customer', 'status', 'payment_status']
    template_name = 'sale_orders/saleorder_form.html'
    success_url = reverse_lazy('saleorder_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = SaleOrderItemFormSet(self.request.POST)
        else:
            context['formset'] = SaleOrderItemFormSet()
        # Pass product prices as JSON for live updates.
        product_prices = {product.id: str(product.unit_price) for product in Product.objects.all()}
        context['product_prices_json'] = json.dumps(product_prices)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context.get('formset')
        # Automatically record the seller.
        form.instance.created_by = self.request.user
        if formset.is_valid():
            self.object = form.save()
            total = Decimal('0.00')
            formset.instance = self.object
            for item in formset.save(commit=False):
                line_total = item.quantity * item.sale_price * (1 - (item.discount / Decimal('100')))
                total += line_total
                item.sale_order = self.object
                item.save()
            self.object.total_amount = total
            self.object.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

# -------------------------------------------------------------------------------
# SaleOrder Update View with Inline Formset for Editing Order Items
# -------------------------------------------------------------------------------
from decimal import Decimal

class SaleOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = SaleOrder
    form_class = SaleOrderForm
    template_name = 'sale_orders/saleorder_form.html'
    success_url = reverse_lazy('saleorder_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            formset = SaleOrderItemFormSet(self.request.POST, instance=self.object)
        else:
            formset = SaleOrderItemFormSet(instance=self.object)
            formset.extra = 0  # Prevent extra blank forms during editing.
        context['formset'] = formset
        product_prices = {product.id: str(product.unit_price) for product in Product.objects.all()}
        context['product_prices_json'] = json.dumps(product_prices)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            total = Decimal('0.00')
            # Loop through each form to compute total using cleaned_data.
            for item_form in formset:
                cleaned_data = item_form.cleaned_data
                # Skip empty forms or those marked for deletion.
                if not cleaned_data or cleaned_data.get('DELETE', False):
                    continue
                quantity = cleaned_data.get('quantity', 0)
                sale_price = cleaned_data.get('sale_price', Decimal('0.00'))
                discount = cleaned_data.get('discount', Decimal('0.00'))
                line_total = quantity * sale_price * (1 - (discount / Decimal('100')))
                total += line_total
            formset.instance = self.object
            formset.save()
            self.object.total_amount = total
            self.object.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

# -------------------------------------------------------------------------------
# SaleOrder Delete View
# -------------------------------------------------------------------------------
class SaleOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = SaleOrder
    template_name = 'sale_orders/saleorder_confirm_delete.html'
    success_url = reverse_lazy('saleorder_list')

# -------------------------------------------------------------------------------
# Sold Products View: Lists sale orders with customer, date, etc.
# -------------------------------------------------------------------------------
@login_required
def Sold_products_view(request):
    sale_orders = SaleOrder.objects.filter(created_by=request.user).select_related('customer').order_by('-order_date')
    context = {'sale_orders': sale_orders}
    return render(request, 'sale_orders/sold_products.html', context)



#-----------------------------------------------------------------------------------
# CASH BOOK
#-----------------------------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from .models import UserFinancialTransaction
from .forms import UserFinancialTransactionForm

@login_required
def user_financial_transaction_view(request):
    if request.method == 'POST':
        form = UserFinancialTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()  # Signal (if any) will update CashBook if approved is True.
            messages.success(request, "Your transaction has been recorded successfully.")
            return redirect('user_financial_transaction_view')
    else:
        form = UserFinancialTransactionForm()
    
    transactions = UserFinancialTransaction.objects.filter(user=request.user).order_by('-date')
    
    # Calculate monthly summary for CASH and BANK accounts
    monthly_summary_qs = UserFinancialTransaction.objects.filter(
        user=request.user, 
        account__in=['CASH', 'BANK']
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        additions=Sum(
            Case(
                When(transaction_type='ADD', then='amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        removals=Sum(
            Case(
                When(transaction_type='REMOVE', then='amount'),
                default=0,
                output_field=DecimalField()
            )
        )
    ).order_by('-month')
    
    # Limit to the last 12 months
    monthly_summary = monthly_summary_qs[:12]
    
    # Calculate grand totals over the displayed months
    grand_totals = monthly_summary.aggregate(
         total_additions=Sum('additions'),
         total_removals=Sum('removals')
    )
    
    return render(request, 'others/user_financial_transaction.html', {
        'form': form,
        'transactions': transactions,
        'monthly_summary': monthly_summary,
        'grand_totals': grand_totals,
    })


@login_required
def transaction_detail_view(request, pk):
    transaction = get_object_or_404(UserFinancialTransaction, pk=pk, user=request.user)
    return render(request, 'others/transaction_detail.html', {'transaction': transaction})


@login_required
def transaction_edit_view(request, pk):
    transaction = get_object_or_404(UserFinancialTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = UserFinancialTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            return redirect('user_financial_transaction_view')
    else:
        form = UserFinancialTransactionForm(instance=transaction)
    
    return render(request, 'others/transaction_edit.html', {'form': form, 'transaction': transaction})


@login_required
def transaction_delete_view(request, pk):
    transaction = get_object_or_404(UserFinancialTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect('user_financial_transaction_view')
    
    return render(request, 'others/transaction_confirm_delete.html', {'transaction': transaction})
