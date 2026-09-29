from django import template

from billing.money import format_credits

register = template.Library()


@register.filter(name="credits")
def credits_filter(micro, places=4):
    return format_credits(micro, int(places))
