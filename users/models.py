from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.conf import settings  # Added to reference the logged-in user

# ------------------------------------------------------------------------------
# Abstract Base Model to include common timestamp fields
# ------------------------------------------------------------------------------
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# ------------------------------------------------------------------------------
# Product Categorization
# ------------------------------------------------------------------------------
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

# ------------------------------------------------------------------------------
# Supplier Model
# ------------------------------------------------------------------------------
def validate_contact_number(value):
    if value:  # Only validate if a value is provided
        if not (value.startswith('07') or value.startswith('06')):
            raise ValidationError('Contact number must start with 07 or 06.')
        if len(value) != 10:
            raise ValidationError('Contact number must be exactly 10 digits long.')
        if not value.isdigit():
            raise ValidationError('Contact number must contain only digits.')

class Supplier(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    contact_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[validate_contact_number]
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# ------------------------------------------------------------------------------
# Customer Model
# ------------------------------------------------------------------------------
class Customer(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    contact_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[validate_contact_number]
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# ------------------------------------------------------------------------------
# Product Model
# ------------------------------------------------------------------------------
class Product(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_stock_level = models.PositiveIntegerField(default=0)  # Reorder threshold
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    
    def __str__(self):
        return self.name

# -------------------------------------------------------------------------------
# Purchase Order and Items Models
# -------------------------------------------------------------------------------
class PurchaseOrder(BaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=100,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending'
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        default=0
    )
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Bank', 'Bank'),
    ]
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='Cash',
        help_text='Select the payment method (Cash or Bank).'
    )
    
    def __str__(self):
        order_id = self.id if self.id else 'Unsaved'
        return f"Purchase Order #{order_id} from {self.supplier.name} on {self.order_date.strftime('%Y-%m-%d')}"


class PurchaseOrderItem(BaseModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchase_items'
    )
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.purchase_price}"
    
    def save(self, *args, **kwargs):
        # When a new purchase item is created, increase the product's stock.
        if not self.pk:
            self.product.quantity_in_stock += self.quantity
            self.product.save()
        super(PurchaseOrderItem, self).save(*args, **kwargs)

# ------------------------------------------------------------------------------  
# Sale Order Model (Optimized)  
# ------------------------------------------------------------------------------  
class SaleOrder(BaseModel):  
    # Linking SaleOrder to the Customer model  
    customer = models.ForeignKey(  
        Customer,  
        on_delete=models.CASCADE,  
        related_name='sale_orders'  
    )  
    # Record the seller (administrator) who creates the sale order  
    created_by = models.ForeignKey(  
        settings.AUTH_USER_MODEL,  
        on_delete=models.SET_NULL,  
        null=True,  
        blank=False,  
        related_name='sale_orders_created'  
    )  
    # Order date (automatically set when the order is created)  
    order_date = models.DateTimeField(auto_now_add=True)  

    # Status of the order (Pending, Completed, Cancelled)  
    STATUS_CHOICES = [  
        ('Pending', 'Pending'),  
        ('Completed', 'Completed'),  
        ('Cancelled', 'Cancelled'),  
    ]  
    status = models.CharField(  
        max_length=100,  
        choices=STATUS_CHOICES,  
        default='Pending',  
    )  

    # Total amount of the sale order  
    total_amount = models.DecimalField(  
        max_digits=10,   
        decimal_places=2,   
        default=0.00  
    )  

    # Payment status (whether the order has been paid or not)  
    PAYMENT_STATUS_CHOICES = [  
        ('Cash', 'Cash'),  
        ('Bank', 'Bank'),
    ]  
    payment_status = models.CharField(  
        max_length=100,  
        choices=PAYMENT_STATUS_CHOICES,  
        default='Unpaid',  
    )  

    def __str__(self):  
        return f"Sale Order #{self.id} for {self.customer.name} on {self.order_date.strftime('%Y-%m-%d')}"  


class SaleOrderItem(BaseModel):
    sale_order = models.ForeignKey(
        SaleOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sale_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Discount percentage for this item"
    )
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.sale_price} (Discount: {self.discount}%)"
    
    def clean(self):
        # Validate that sufficient stock is available for this sale.
        if not self.pk and self.product.quantity_in_stock < self.quantity:
            raise ValidationError(f"Not enough stock for product: {self.product.name}")
    
    def save(self, *args, **kwargs):
        # Run validation first.
        self.clean()
        if not self.pk:
            # Deduct sold quantity from product stock.
            self.product.quantity_in_stock -= self.quantity
            self.product.save()
        super(SaleOrderItem, self).save(*args, **kwargs)

# ------------------------------------------------------------------------------
# Invoice and Payment Models
# ------------------------------------------------------------------------------
class Invoice(BaseModel):
    sale_order = models.OneToOneField(
        SaleOrder,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Invoice #{self.id} for Sale Order #{self.sale_order.id}"

class Payment(BaseModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, help_text="e.g., Cash, Credit Card, Bank Transfer")
    
    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date.strftime('%Y-%m-%d')}"

# ------------------------------------------------------------------------------
# Sale Return Model (For Handling Customer Returns)
# ------------------------------------------------------------------------------
class SaleReturn(BaseModel):
    sale_order_item = models.ForeignKey(
        SaleOrderItem,
        on_delete=models.CASCADE,
        related_name='returns'
    )
    return_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"Return of {self.quantity} x {self.sale_order_item.product.name} on {self.return_date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # When a return is processed, add the returned quantity back to stock.
            self.sale_order_item.product.quantity_in_stock += self.quantity
            self.sale_order_item.product.save()
        super(SaleReturn, self).save(*args, **kwargs)

# ------------------------------------------------------------------------------
# Optional Promotion Model (For Special Offers)
# ------------------------------------------------------------------------------
class Promotion(BaseModel):
    name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off from {self.start_date} to {self.end_date})"

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    uidb64 = models.CharField(max_length=64, blank=True, null=True)  # Store UID base64
    token = models.CharField(max_length=128, blank=True, null=True)  # Store token
    expires_at = models.DateTimeField(blank=True, null=True)  # Expiration time for the code and token
    request_token = models.UUIDField(default=uuid4, editable=False)  # Unique request token

    def __str__(self):
        return f"Reset Code for {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at if self.expires_at else False

    def delete_if_expired_or_used(self, token_used=False):
        if self.is_expired() or token_used:
            self.delete()


#-------------------------------------------------------------------------------
#CASH BOOK 
#-------------------------------------------------------------------------------

class UserFinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('ADD', 'Addition'),   # Money added to the business
        ('REMOVE', 'Removal'), # Money removed from the business
    ]
    ACCOUNT_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_transactions')
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    account = models.CharField(max_length=4, choices=ACCOUNT_CHOICES, default='CASH')
    approved = models.BooleanField(default=False)  # Only approved transactions go to cash book
    
    def __str__(self):
        return f"{self.user.username}: {self.get_transaction_type_display()} of {self.amount} on {self.date:%Y-%m-%d}"
