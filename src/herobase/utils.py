# -*- coding: utf-8 -*-
from datetime import date

from django.contrib.auth.hashers import mask_hash, BasePasswordHasher
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _


class PlainTextPasswordHasher(BasePasswordHasher):
    """
    I am an incredibly insecure algorithm you should *never* use;
    I am only for faster tests.
    """
    algorithm = "plain"

    def salt(self):
        return ""

    def encode(self, password, salt):
        return password

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
            login_url = reverse('auth_login')
            url = request.build_absolute_uri()  # this should be request.path
            return HttpResponseRedirect("%s?next=%s" % (login_url, url))
        else:
            return function(request, *args, **kwargs)
    return decorated


def yearsago(years):
    d = date.today()
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # february 29th
        return d.replace(year=d.year - years, day=d.day - 1)


def is_minimum_age(date_of_birth):
    return date_of_birth <= yearsago(15)


def is_legal_adult(date_of_birth):
    return date_of_birth <= yearsago(18)
