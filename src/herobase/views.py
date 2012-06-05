# Create your views here.
from itertools import chain
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils import simplejson
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator

from django.views.generic import ListView
from django.views.generic.edit import CreateView
from filters import QuestFilter
from herobase.forms import QuestCreateForm, UserProfileEdit, UserProfilePrivacyEdit
from herobase.models import Quest, Adventure, CLASS_CHOICES
import logging
from django.db.models import Count, Sum

logger = logging.getLogger('youarehero.herobase')

def quest_list_view(request):
    f = QuestFilter(request.GET, queryset=Quest.objects.all())
    return render(request, 'herobase/quest/list.html', {
        'filter': f,
    })

class QuestCreateView(CreateView):
    context_object_name = "quest"
    form_class = QuestCreateForm
    template_name = "herobase/quest/create.html"
    success_url = '../%(id)s/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(QuestCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

def quest_detail_view(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    if not request.user.is_anonymous():
        try:
            adventure = quest.adventure_set.get(user=request.user)
        except Adventure.DoesNotExist:
            adventure = None
    else:
        adventure = None
    context = {
        'quest': quest,
        'adventure': adventure,
    }

    return render(request, "herobase/quest/detail.html", context)

def home_view(request):
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {'open_quests':
        Quest.objects.filter(state=Quest.STATE_OPEN)})


@login_required
def hero_home_view(request):
    user = request.user
    quests = sorted(chain(user.created_quests.order_by('-created'),
            Quest.objects.filter(adventure__user=user).exclude(adventure__user=user, adventure__state=Adventure.STATE_HERO_CANCELED)),
            key=lambda instance: instance.created, reverse=True)
    return render(request, 'herobase/hero_home.html',
            {'user': user,
             'profile': user.get_profile(),
             'quests': quests
             })

@require_POST
@login_required
def quest_update(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)

    if 'action' in request.POST:
        action = request.POST['action']
        try:
            quest.process_action(request, action)
        except ValueError, e:
            messages.error(request, e.message)
        except PermissionDenied, e:
            messages.error(request, e.message)
    else:
        messages.error(request, 'No action submitted.')

    return HttpResponseRedirect(reverse('quest-detail', args=(quest.pk, )))

@require_POST
@login_required
def adventure_update(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)

    if 'adventure_id' in request.POST:
        adventure_id = request.POST['adventure_id']
        adventure = get_object_or_404(Adventure, pk=adventure_id)

    if adventure not in quest.adventure_set.all():
        raise Http404

    if 'action' in request.POST:
        action = request.POST['action']
        try:
            adventure.process_action(request, action)
        except ValueError, e:
            messages.error(request, e.message)
        except PermissionDenied, e:
            messages.error(request, e.message)
    else:
        messages.error(request, 'No action submitted.')

    return HttpResponseRedirect(reverse('quest-detail', args=(quest.pk, )))


def userprofile_public(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'herobase/userprofile/public.html', {
        'user': user
    })

@login_required
def userprofile_edit(request):
    user = request.user
    form = UserProfileEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile successfully changed')
    return render(request, 'herobase/userprofile/edit.html', {
        'user': user,
        'form': form
    })

@login_required
def userprofile_privacy_settings(request):
    user = request.user
    form = UserProfilePrivacyEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Privacy settings successfully changed')
        return HttpResponseRedirect('.')
    return render(request, 'herobase/userprofile/privacy_settings.html', {
        'user': user,
        'form': form
    })


def leader_board(request):
    total = User.objects.select_related().order_by('-userprofile__experience')
    by_class = {}
    for hero_class, class_name in CLASS_CHOICES:
        by_class[class_name] = User.objects.select_related()\
                                         .filter(userprofile__hero_class=hero_class)\
                                         .order_by('-userprofile__experience')

    by_quest_class = {}
    for hero_class, class_name in CLASS_CHOICES:
        by_quest_class[class_name] = User.objects.filter(adventures__quest__hero_class=hero_class,
            adventures__quest__state=Quest.STATE_OWNER_DONE)\
            .annotate(class_experience=Sum('adventures__quest__experience'))\
            .order_by('-class_experience')

    return render(request, "herobase/leader_board.html", {'total': total,
                                                         'by_class': by_class,
                                                         'by_quest_class': by_quest_class,
                                                         })

def random_stats(request):
    user = request.user
    class_choices = dict(CLASS_CHOICES)

    adventure_count_by_class = []
    for choice, count in user.adventures.values_list('quest__hero_class').annotate(Count('quest__hero_class')):
        adventure_count_by_class.append((class_choices[choice], count))

    open_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OPEN).values_list('hero_class').annotate(Count('hero_class')):
        open_quest_types.append((class_choices[choice], count))

    completed_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OWNER_DONE).values_list('hero_class').annotate(Count('hero_class')):
        open_quest_types.append((class_choices[choice], count))

    context = {
        'adventure_count_by_class': adventure_count_by_class,
        'open_quest_types': open_quest_types,
        'completed_quest_types': completed_quest_types,
        }
    for key in context:
        context[key] = mark_safe(simplejson.dumps(list(context[key])))

    context.update({
        'quests_completed': user.adventures.filter(quest__state=Quest.STATE_OWNER_DONE).count()
    })

    return render(request, 'herobase/stats.html', context)