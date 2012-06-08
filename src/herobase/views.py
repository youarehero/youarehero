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
from herobase.models import Quest, Adventure, CLASS_CHOICES, UserProfile
import logging
from django.db.models import Count, Sum

logger = logging.getLogger('youarehero.herobase')

def quest_list_view(request):
    f = QuestFilter(request.GET, queryset=Quest.objects.order_by('-created'))
    return render(request, 'herobase/quest/list.html', {
        'filter': f,
        'quests': f.qs,
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

@login_required
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

def abstract(request):
    return render(request, "herobase/abstract.html")

def hero_classes(request):
    return render(request, "herobase/hero_classes.html")

@login_required
def hero_home_view(request):
    user = request.user
    return render(request, 'herobase/hero_home.html',
            {
             #'profile': user.get_profile(),
             'quests_active': user.created_quests.active().order_by('-created'),
             'quests_old': user.created_quests.inactive().order_by('-created'),
             'quests_joined': Quest.objects.active().filter(adventure__user=user).exclude(adventure__user=user, adventure__state=Adventure.STATE_HERO_CANCELED)
             })

@login_required
def quest_my(request):
    user = request.user
    return render(request, 'herobase/quest/my.html',
            {
            #'profile': user.get_profile(),
            'quests_active': user.created_quests.active().order_by('-created'),
            'quests_old': user.created_quests.inactive().order_by('-created'),
            'quests_joined': Quest.objects.active().filter(adventure__user=user).exclude(adventure__user=user, adventure__state=Adventure.STATE_HERO_CANCELED)
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

@login_required
def userprofile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    rank = UserProfile.objects.filter(experience__gt=user.get_profile().experience).count() + 1
    hero_completed_quests = []
    class_choices = dict(CLASS_CHOICES)
    color_dict = { 5: '#e8e8e8',
                   1: '#ccffa7',
                   2: '#fff9b4',
                   3: '#ffa19b',
                   4: '#bdcaff'}
    colors = []
    for choice, count in user.adventures\
            .filter(state=Adventure.STATE_OWNER_DONE)\
            .values_list('quest__hero_class')\
            .annotate(Count('quest__hero_class')):
        colors.append(color_dict[choice])
        hero_completed_quests.append((class_choices[choice], count))


    return render(request, 'herobase/userprofile/detail.html', {
        'user': user,
        'rank': rank,
        'colors': mark_safe(simplejson.dumps(colors)),
        'completed_quest_count': user.adventures.filter(state=Adventure.STATE_OWNER_DONE).count(),
        'hero_completed_quests': mark_safe(simplejson.dumps(hero_completed_quests)),
    })

@login_required
def userprofile_edit(request):
    user = request.user
    form = UserProfileEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile successfully changed')
    return render(request, 'herobase/userprofile/edit.html', {
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
        'form': form
    })

@login_required
def leader_board(request):
    total = User.objects.select_related().filter(userprofile__experience__gt=0).order_by('-userprofile__experience')
#    by_class = {}
#    for hero_class, class_name in CLASS_CHOICES:
#        by_class[class_name] = User.objects.select_related()\
#                                         .filter(userprofile__hero_class=hero_class)\
#                                         .order_by('-userprofile__experience').filter('userprofile__experience')

    top_creators = User.objects.filter(created_quests__state=Quest.STATE_OWNER_DONE).annotate(quest_count=Count('created_quests')).filter(quest_count__gt=0).order_by('-quest_count')
#    by_quest_class = {}
#    for hero_class, class_name in CLASS_CHOICES:
#        by_quest_class[class_name] = User.objects.filter(
#            adventures__quest__hero_class=hero_class,
#            adventures__state=Adventure.STATE_OWNER_DONE,
#            adventures__quest__state=Quest.STATE_OWNER_DONE)\
#            .annotate(class_experience=Sum('adventures__quest__experience'))\
#            .order_by('-class_experience')

    return render(request, "herobase/leader_board.html", {'total': total,
#                                                         'by_class': by_class,
                                                         'top_creators': top_creators
#                                                         'by_quest_class': by_quest_class,
                                                         })
@login_required
def random_stats(request):
    user = request.user
    class_choices = dict(CLASS_CHOICES)
    color_dict = { 5: '#e8e8e8',
                   1: '#ccffa7',
                   2: '#fff9b4',
                   3: '#ffa19b',
                   4: '#bdcaff'}



    hero_completed_quests = []
    for choice, count in user.adventures\
        .filter(quest__state=Quest.STATE_OWNER_DONE)\
        .filter(state=Adventure.STATE_OWNER_DONE)\
        .values_list('quest__hero_class')\
        .annotate(Count('quest__hero_class')):
        hero_completed_quests.append((class_choices[choice], count))

    colors0 = []
    open_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OPEN).values_list('hero_class').annotate(Count('hero_class')):
        open_quest_types.append((class_choices[choice], count))
        colors0.append(color_dict[choice])

    colors1 = []
    completed_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OWNER_DONE).values_list('hero_class').annotate(Count('hero_class')):
        completed_quest_types.append((class_choices[choice], count))
        colors1.append(color_dict[choice])

    context = {
        'hero_completed_quests': hero_completed_quests,
        'open_quest_types': open_quest_types,
        'completed_quest_types': completed_quest_types,
        'colors0': colors0,
        'colors1': colors1,
        }
    for key in context:
        context[key] = mark_safe(simplejson.dumps(list(context[key])))

    context.update({
        'quests_completed': user.adventures.filter(quest__state=Quest.STATE_OWNER_DONE).count()
    })

    return render(request, 'herobase/stats.html', context)

def signups(request):
    if request.user.is_authenticated() and request.user.is_staff:
        return HttpResponse('\n'.join('%s: %s' % (u.date_joined, u.username) for u in User.objects.order_by('-date_joined')[:10]), mimetype='text/plain')
    else:
        raise Http404()