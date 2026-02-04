from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allows accessing a dictionary value by a dynamic variable key."""
    if dictionary:
        return dictionary.get(key)
    return None