from models import QuestRating, SKILLS
from herobase.models import Quest

def rate_quest(user, quest, action):
    QuestRating.rate(user, quest, action)


class MergedQuerySet(object):
    def __init__(self, *querysets):
        self.querysets = querysets

    def count(self):
        return sum(qs.count() for qs in self.querysets)

    def __iter__(self):
        while True:
            for qs in self.querysets:
                yield(qs)


def recommend(user, fields=('title', 'description', 'state', 'location'),
        queryset=None, order_by=None):
    queryset = queryset or Quest.objects.active()
    local = queryset.filter(location=user.get_profile().location)
    remote = queryset.filter(location='')
    queryset = local | remote
    return recommend_for_user(user, fields=fields, queryset=queryset,
            order_by=order_by)

def recommend_remote(user, fields=('title', 'description', 'state'),
        queryset=None, order_by=None):
    queryset = queryset or Quest.objects.active()
    queryset = queryset.filter()
    return recommend_for_user(user, fields=fields, queryset=queryset,
            order_by=order_by)

def recommend_local(user, fields=('title', 'description', 'state'),
        queryset=None, order_by=None):
    queryset = queryset or Quest.objects.active()
    queryset = queryset.filter()
    return recommend_for_user(user, fields=fields, queryset=queryset,
            order_by=order_by)

def recommend_for_user(user, fields=('title', 'description', 'state'),
        queryset=None, order_by=None):
    queryset = queryset or Quest.objects.active()

    order_fields = ['-weight']
    if order_by:
        order_fields.extend(order_by)
    
    result_fields = ['weight', 'profile__average', 'id', 'pk']
    if fields:
        result_fields = list(fields) + result_fields

    up = user.combined_profile

    up_deltas = {}
    up_average = up.average
    for skill in SKILLS:
        up_deltas[skill] = getattr(up, skill) - up_average

    up_root_sum_of_squares = sum(w**2 for w in up_deltas.values()) ** 0.5

    denominator = []
    for skill in SKILLS:
        denominator.append('(%s * delta_%s)' % (up_deltas[skill], skill))
    denominator_sql = '(%s)' % (' + '.join(denominator))

    numerator_sql = '%s * root_sum_of_squares' % up_root_sum_of_squares

    sql = '(%s) / (%s)' % (denominator_sql, numerator_sql) # fixme DIV BY ZERO
    return (queryset
            .select_related('profile')
            .extra(select={'weight': sql})
            .order_by(*order_fields)
            .values(*result_fields))
