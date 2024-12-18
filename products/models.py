from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, Sum, DecimalField
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='subcategories', 
        blank=True, 
        null=True
    )  # Self-referential relationship for subcategories

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name

    class Meta:
        verbose_name_plural = "Categories"  # Fix plural naming in admin
        unique_together = ('name', 'parent')  # Prevent duplicate subcategories under the same parent

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')  # Ensure Pillow is installed for ImageField
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)  # To track inventory
    slug = models.SlugField(max_length=255, unique=True)  # SEO-friendly URL
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time
    updated_at = models.DateTimeField(auto_now=True)  # Track update time

    def __str__(self):
        return self.name

    def update_stock(self, quantity):
        """ Method to update stock after purchase """
        self.stock -= quantity
        if self.stock < 0:
            raise ValidationError(f"Not enough stock for {self.name}. Only {self.stock + quantity} available.")
        self.save()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)  # Track if the cart has been converted to an order
    updated_at = models.DateTimeField(auto_now=True)  # Track last cart update time

    def total_price(self):
        # Using annotate for better performance instead of Python sum()
        return self.items.aggregate(total=Sum(F('quantity') * F('product__price'), output_field=DecimalField()))['total'] or 0

    def __str__(self):
        return f"Cart for {self.user.username}"

    def update_stock_after_checkout(self):
        """ Method to update stock after checkout process """
        for item in self.items.all():
            item.product.update_stock(item.quantity)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def clean(self):
        # Validate quantity against stock
        if self.quantity > self.product.stock:
            raise ValidationError(f"Cannot add more than {self.product.stock} of {self.product.name} to the cart.")

    def save(self, *args, **kwargs):
        self.clean()  # Call clean method to validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for the item."""
        return self.product.price * self.quantity
