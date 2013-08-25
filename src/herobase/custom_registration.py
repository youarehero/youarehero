from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from registration import signals
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile

from herobase.models import UserProfile
from herobase.utils import is_minimum_age


class Form(RegistrationForm):
    username = forms.CharField(
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'required'}),
        label=_("Username")
    )
    date_of_birth = forms.DateField()


class Backend(object):
    def register(self, request, **kwargs):
        if not is_minimum_age(kwargs['date_of_birth']):
            # We can't redirect here because django-registration ignores it
            # Instead, we return None and redirect in the
            # post_registration_redirect method.
            #
            # This is ugly and we should upgrade django-registration soon
            return None

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        new_user = RegistrationProfile.objects.create_inactive_user(
            kwargs['username'],
            kwargs['email'],
            kwargs['password1'],
            site
        )

        profile = UserProfile(
            user=new_user,
            date_of_birth=kwargs['date_of_birth']
        )
        profile.save()

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activated = RegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated,
                                        request=request)
        return activated

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.

        """
        return Form

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        if not isinstance(user, User):
            # We are here because register(..) returned None.
            # This is a hack. Explanation in the register method.
            return ('registration_below_minimum_age', (), {})
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.

        """
        return ('registration_activation_complete', (), {})
