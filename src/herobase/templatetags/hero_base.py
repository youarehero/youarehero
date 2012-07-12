# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from herobase.models import Quest

register = template.Library()

@register.simple_tag
def user_link(user):
#    return mark_safe('<a href="%s">M</a>' % reverse('message-to', args=(user.pk, )))
    return ''

@register.assignment_tag(takes_context=True)
def suggest_quests(context, count):
    try:
        count = int(count)
    except ValueError:
        count = 3
    request = context['request']
    return Quest.get_suggested_quests(request.user, count)