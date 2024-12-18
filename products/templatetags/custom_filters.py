from django import template

register = template.Library()

@register.simple_tag
def get_products_for_category(category, category_products):
    return category_products.get(category, [])