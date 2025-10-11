from django import template
import ast

register = template.Library()

@register.filter(name='as_widget')
def as_widget(field, attrs):
    """Render a form field as a widget with additional HTML attributes."""
    if isinstance(attrs, str):
        attrs = ast.literal_eval(attrs)
    return field.as_widget(attrs=attrs)