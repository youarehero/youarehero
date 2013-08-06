from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from herobase.models import Quest


class Organization(models.Model):
    user = models.OneToOneField(User, related_name="is_organization")
    description = models.TextField()

    def get_absolute_url(self):
        return reverse("organization_detail", args=(self.user.username, ))

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return self.user.username

    @property
    def quests(self):
        return self.user.created_quests.all()