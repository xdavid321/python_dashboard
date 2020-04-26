from django import template

register = template.Library()

@register.filter
def get_item(dic, key):
    return dic[key]

@register.filter
def get_list_item(lst, key):
    return lst[key]