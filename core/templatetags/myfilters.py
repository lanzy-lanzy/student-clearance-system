from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter(name='has_attr')
def has_attr(obj, attr_name):
    """Checks if an object has the specified attribute"""
    return hasattr(obj, attr_name)

@register.filter(name='rejectattr')
def rejectattr(value, attr_value_pair):
    """
    Filter a list of objects based on an attribute not equal to a value
    Usage: {{ students|rejectattr:"is_approved,True" }}
    """
    try:
        attr, val = attr_value_pair.split(',')
        val = val.strip().lower() == 'true'  # Convert string to boolean
        return [item for item in value if not getattr(item, attr, None) == val]
    except (ValueError, AttributeError):
        return value

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None

    # Convert key to the appropriate type if it's a string representation of an integer
    if isinstance(key, str) and key.isdigit():
        key = int(key)

    return dictionary.get(key)
