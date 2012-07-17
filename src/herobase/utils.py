# -*- coding: utf-8 -*-
"""
Up to now here is only a plain password hasher for faster tests. Never use it elsewhere.
"""
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.hashers import mask_hash, BasePasswordHasher
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models

class PlainTextPasswordHasher(BasePasswordHasher):
    """
    I am an incredibly insecure algorithm you should *never* use;
    I am only for faster tests.
    """
    algorithm = "plain"

    def salt(self):
        raise Exception("Plaintext hasher is only meant for running tests")

    def encode(self, password, salt):
        raise Exception("Plaintext hasher is only meant for running tests")

    def verify(self, password, encoded):
        return password == encoded.split('$')[2]

    def safe_summary(self, encoded):
        return SortedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), mask_hash(encoded, show=3)),
        ])



def login_required(function):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def decorated(request, *args, **kwargs):

        if not request.user.is_authenticated():
            if request.is_mobile:
                login_url = reverse('auth_login-m')
            else:
                login_url = reverse('auth_login')
            url = request.build_absolute_uri() # this should be request.path
            return HttpResponseRedirect("%s?next=%s" % (login_url, url))
        else:
            return function(request, *args, **kwargs)
    return decorated