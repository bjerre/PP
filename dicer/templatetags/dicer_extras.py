__author__ = 'jonesy'
from django import template
from dicer.models import Category

register = template.Library()

@register.inclusion_tag('dicer/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all(), 'act_cat': cat}