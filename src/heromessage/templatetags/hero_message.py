# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def message_user(user):
    return mark_safe('<a href="%s"><i class="icon-yah-mail icon-20"></i></a>' % reverse('message_to', args=(user.pk, )))