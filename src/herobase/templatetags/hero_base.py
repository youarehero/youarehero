# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def user_link(user):
#    return mark_safe('<a href="%s">M</a>' % reverse('message-to', args=(user.pk, )))
    return ''