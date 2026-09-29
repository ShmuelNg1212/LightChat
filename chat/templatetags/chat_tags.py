from django import template
from django.utils.safestring import mark_safe

from chat.markdown import render

register = template.Library()


@register.filter
def markdown(text):
    return mark_safe(render(text))
