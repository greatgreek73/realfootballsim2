from django import template

register = template.Library()

@register.filter
def format_trait_name(value):
    """Convert trait names from snake_case to Title Case"""
    if not value:
        return ''
    return value.replace('_', ' ').title()

@register.filter
def multiply_by_100(value):
    """Multiply a decimal value by 100 for percentage display"""
    try:
        return float(value) * 100
    except (ValueError, TypeError):
        return 0