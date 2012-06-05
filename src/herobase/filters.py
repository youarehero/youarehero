import django_filters
from django.utils.translation import ugettext_lazy as _
from herobase.models import Quest, CLASS_CHOICES

NO_CHOICE = (('', _('Any')),)

class QuestFilter(django_filters.FilterSet):
    hero_class = django_filters.ChoiceFilter(choices=NO_CHOICE + CLASS_CHOICES)
    level = django_filters.ChoiceFilter(lookup_type='contains', choices=NO_CHOICE + Quest.QUEST_STATES)
    state = django_filters.ChoiceFilter(choices=NO_CHOICE + Quest.QUEST_LEVELS)

    def is_filtered(self):
        return any(self.data.values())

    model = Quest
    fields = ['level', 'state', 'hero_class', 'due_date', 'title', 'description']
    class Meta:
        order_by = ['title', 'experience', 'due_date', 'hero_class', 'state']