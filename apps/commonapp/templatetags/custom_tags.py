import json
from datetime import date

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def tag_welcomenote(context, cookiename):
    request = context["request"]
    if not request.user.is_authenticated:
        return "Welcome, Guest"

    user = request.user
    today = date.today()
    name = user.get_full_name() or user.username

    return f"Welcome {name}, {today.strftime('%d-%B-%Y')}"
