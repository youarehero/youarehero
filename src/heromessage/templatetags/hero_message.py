# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

register = template.Library()

@register.simple_tag
def message_user(user, size=20):
    mail_link = '<a href="%(url)s" data-toggle="tooltip" data-title="%(tooltip)s"><i class="icon-yah-mail icon-%(size)s"></i></a>' % {
        'url': reverse('message_to', args=(user.pk, )),
        'tooltip': ugettext(u'Send message to %(username)s') % {'username': user.username},
        'size': size,
    }
    return mark_safe(mail_link)

@register.simple_tag
def message_team(team, size=20):
    mail_link = '<a href="%(url)s" data-toggle="tooltip" data-title="%(tooltip)s"><i class="icon-yah-mail icon-%(size)s"></i></a>' % {
        'url': reverse('message_team_to', args=(team, )),
        'tooltip': ugettext(u'Send message to team %(team)s') % {'team': team},
        'size': size,
    }
    return mark_safe(mail_link)
