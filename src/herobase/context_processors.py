# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from herobase.forms import UserAuthenticationForm
from herobase.models import Quest

def login_form(request):
    """Add login_form to template context if the user is not authenticated."""
    if request.user.is_anonymous():
        return {'login_form': UserAuthenticationForm(request)}
    return {}



def butler_text(request):
    active = lambda *args, **kwargs: reverse(*args, **kwargs) == request.path
    below = lambda *args, **kwargs: request.path.startswith(reverse(*args, **kwargs))

    if active('home'):
        text = 'Auf der Startseite'
    else:
        text = 'Wollen Sie mich ärgern?'
    return {'butler_default_text': text}