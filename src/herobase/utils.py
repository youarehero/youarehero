# -*- coding: utf-8 -*-
from django.contrib.auth.hashers import mask_hash, BasePasswordHasher
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models

class PlainTextPasswordHasher(BasePasswordHasher):
    """
    I am an incredibly insecure algorithm you should *never* use;
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


def generate_chainable_manager(qs_class):
    class ChainableManager(models.Manager):
        def __init__(self):
            super(ChainableManager,self).__init__()
            self.queryset_class = qs_class

        def get_query_set(self):
            return self.queryset_class(self.model)

        def __getattr__(self, attr, *args):
            try:
                return getattr(self.__class__, attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainableManager()


