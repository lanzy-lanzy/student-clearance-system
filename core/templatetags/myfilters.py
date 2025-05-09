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

@register.filter(name='semester_display')
def semester_display(semester_code):
    """
    Convert semester code to display text
    Usage: {{ semester_code|semester_display }}
    """
    semester_map = {
        "1ST_MID": "1st Sem - Midterm",
        "1ST_FIN": "1st Sem - Final",
        "2ND_MID": "2nd Sem - Midterm",
        "2ND_FIN": "2nd Sem - Final",
        "SUM": "Summer",
        # Legacy codes for backward compatibility
        "1ST": "First Semester",
        "2ND": "Second Semester"
    }
    return semester_map.get(semester_code, semester_code)
