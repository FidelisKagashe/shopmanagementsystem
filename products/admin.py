from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Cart, CartItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'image_preview', 'stock', 'slug', 'created_at', 'updated_at')  # Added additional fields
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('name',)  # Optional: Order products by name

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_ordered', 'updated_at')  # Display the user and order status
    search_fields = ('user__username',)
    ordering = ('-updated_at',)  # Order carts by the most recent updates

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')  # Display the cart, product, and quantity
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart', 'product')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
