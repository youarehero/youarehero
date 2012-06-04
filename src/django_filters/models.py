from django import forms
import django_filters
from herobase import widgets
from herobase.models import Quest, CLASS_CHOICES

class QuestFilter(django_filters.FilterSet):

#    title = django_filters.CharFilter(lookup_type='contains')
#    due_date = django_filters.DateFilter(lookup_type='lt')

    hero_class = django_filters.ChoiceFilter()
    level = django_filters.ChoiceFilter(lookup_type='contains')
    state = django_filters.ChoiceFilter()

    model = Quest
    fields = ['level', 'state', 'hero_class', 'due_date', 'title', 'description']

    class Meta:
        order_by = ['title', 'experience', 'due_date', 'hero_class', 'state']

    CHOICES_FOR_HERO_CLASS = [
        ('', 'All Classes'),
    ]
    CHOICES_FOR_HERO_CLASS.extend(list(CLASS_CHOICES))

    CHOICES_FOR_STATE = [
        ('', 'All States'),
    ]
    CHOICES_FOR_STATE.extend(list(Quest.QUEST_STATES))

    CHOICES_FOR_LEVEL = [
        ('', 'All Levels'),
    ]
    CHOICES_FOR_LEVEL.extend(list(Quest.QUEST_LEVELS))

    def __init__(self, *args, **kwargs):
        super(QuestFilter, self).__init__(*args, **kwargs)

        self.filters['hero_class'].extra.update(
                {
                'choices': self.CHOICES_FOR_HERO_CLASS
            })

        self.filters['state'].extra.update(
                {
                'choices': self.CHOICES_FOR_STATE
            })

        self.filters['level'].extra.update(
                {
                'choices': self.CHOICES_FOR_LEVEL
            })