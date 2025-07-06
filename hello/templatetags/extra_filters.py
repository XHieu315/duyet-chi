from django import template
register = template.Library()

@register.filter
def get(dict_data, key):
    return dict_data.get(key)

@register.filter
def format_vnd(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", ".")
    except:
        return value
