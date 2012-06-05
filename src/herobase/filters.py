import django_filters
from herobase.models import Quest, CLASS_CHOICES

class QuestFilter(django_filters.FilterSet):
    hero_class = django_filters.ChoiceFilter()
    level = django_filters.ChoiceFilter(lookup_type='contains')
    state = django_filters.ChoiceFilter()

    model = Quest
    fields = ['level', 'state', 'hero_class', 'due_date', 'title', 'description']

    class Meta:
        order_by = ['title', 'experience', 'due_date', 'hero_class', 'state']

    CHOICES_FOR_HERO_CLASS = (('', 'All Classes'),) + CLASS_CHOICES
    CHOICES_FOR_STATE = (('', 'All States'),) + Quest.QUEST_STATES
    CHOICES_FOR_LEVEL = (('', 'All Levels'),) + Quest.QUEST_LEVELS

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