# Create your views here.
from itertools import chain
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
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
from herobase.models import Quest, Adventure
import logging
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
    success_url = './%(id)s'

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
    return render(request, 'herobase/userprofile/privacy_settings.html', {
        'user': user,
        'form': form
    })



