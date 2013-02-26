# -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class DjangoModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            print "GETTING"
            return User.objects.select_related('profile').get(pk=user_id)
        except User.DoesNotExist:
            return None

class EmailAuthBackend(DjangoModelBackend):
    """Custom Authentication Backend for user validation with email addy and password."""
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

