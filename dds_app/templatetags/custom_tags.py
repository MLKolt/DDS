from django import template

register = template.Library()


# Кастомный фильтр, чтобы получать имя поля в шаблоне
@register.filter
def get_field_display(obj, field_name):
    return getattr(obj, field_name)
