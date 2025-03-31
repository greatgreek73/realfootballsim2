from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Фильтр шаблона для получения значения из словаря по ключу
    Пример использования: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key)
