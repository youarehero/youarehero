"""
Filter classes for django-filters. Only the Quest list view use django-filters.
"""
import django_filters
from django.utils.translation import ugettext_lazy as _
from herobase.models import Quest, CLASS_CHOICES

NO_CHOICE = (('', _('Any')),)

class QuestFilter(django_filters.FilterSet):
    """Django-filters filter class. Defines the filters for the quest-list-view."""
    title = django_filters.CharFilter(lookup_type="icontains")

    def is_filtered(self):
        return any(self.data.values())

    model = Quest
    fields = ['level', 'state', 'expiration_date', 'title', 'description']
    class Meta:
        order_by = ['title', 'expiration_date', 'state']