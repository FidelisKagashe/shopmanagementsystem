from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Cart, CartItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'full_hierarchy')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)  # Filter by parent category to navigate subcategories easily

    def full_hierarchy(self, obj):
        """Display the full hierarchy of the category for better understanding."""
        hierarchy = []
        current = obj
        while current:
            hierarchy.insert(0, current.name)
            current = current.parent
        return " > ".join(hierarchy)
    full_hierarchy.short_description = 'Category Hierarchy'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'image_preview', 'stock', 'slug', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name')
    ordering = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_ordered', 'total_price', 'updated_at')
    search_fields = ('user__username',)
    ordering = ('-updated_at',)
    list_filter = ('is_ordered',)

    def total_price(self, obj):
        """Show total price for the cart."""
        return obj.total_price()
    total_price.short_description = 'Total Price'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart', 'product')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
