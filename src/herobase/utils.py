# -*- coding: utf-8 -*-
"""
Up to now here is only a plain password hasher for faster tests. Never use it elsewhere.
"""
from django.contrib.auth.hashers import mask_hash, BasePasswordHasher
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