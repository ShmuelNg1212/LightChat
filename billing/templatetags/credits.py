from django import template

from billing.money import format_credits

register = template.Library()


@register.filter(name="credits")
def credits_filter(micro, places=4):
    return format_credits(micro, int(places))


@register.filter
def abs_credits(micro, places=4):
    return format_credits(abs(micro), int(places)) if micro is not None else format_credits(None)
