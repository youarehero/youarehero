# Create your views here.
from django.contrib.auth.models import User
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
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from herobase.forms import QuestCreateForm, UserProfileEdit
from herobase.models import Quest, Adventure
from registration.forms import RegistrationForm


class QuestListView(ListView):
    context_object_name = "quests"
    queryset = Quest.objects.filter(state=Quest.STATE_OPEN)
    template_name = "herobase/quest/list.html"


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

class QuestDetailView(DetailView):
    context_object_name = "quest"
    model = Quest

    def get_context_data(self, **kwargs):
        try:
            adventure = self.object.adventure_set.get(user=self.request.user)
        except Adventure.DoesNotExist:
            adventure = None
        kwargs['adventure'] = adventure
        return super(QuestDetailView, self).get_context_data(**kwargs)

    def get_template_names(self):
        if self.object.owner == self.request.user:
            return ['herobase/quest/detail_for_author.html']
        else:
            return ['herobase/quest/detail_for_hero.html']

def home_view(request):
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {'open_quests':
        Quest.objects.filter(state=Quest.STATE_OPEN)})


@login_required
def hero_home_view(request):
    user = request.user
    return render(request, 'herobase/hero_home.html',
            {'user': user,
             'profile': user.get_profile(),
             'adventures': user.adventures.exclude(state=Adventure.STATE_CANCELED).order_by('-created'),
             'created_quests': user.created_quests.order_by('-created')})

@require_POST
@login_required
def adventure_update(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    if 'apply' in request.POST:
        if request.user == quest.owner:
            messages.error(request, "You can't participate in your own quest.")
        elif request.user in quest.active_heroes():
            messages.info(request, 'You are already applying for the quest "%s".' % quest.title)
        else:
            adventure, created = Adventure.objects.get_or_create(user=request.user, quest=quest)
            adventure.state = Adventure.STATE_HERO_APPLIED
            adventure.save()
            messages.success(request, 'You are a hero!')
        return HttpResponseRedirect(reverse('quest-detail', args=(quest.pk, )))
    elif 'cancel' in request.POST:
        if request.user == quest.owner:
            quest.state = Quest.STATE_OWNER_CANCELED
            quest.save()
            messages.info(request, mark_safe('Quest <em>{0}</em> abgebrochen.'.format(escape(quest.title))))
        elif request.user in quest.heroes.all(): # TODO : only allow cancel if it makes sense (not done, etc)
            adventure = quest.adventure_set.get(user=request.user)
            adventure.state = Adventure.STATE_CANCELED
            adventure.save()
            messages.info(request, mark_safe('Quest <em>{0}</em> abgebrochen.'.format(escape(quest.title))))
        return HttpResponseRedirect(reverse("home"))
>>>>>>> Stashed changes:src/herobase/views.py

def decorator(f):
    def decorated(*args, **kwargs):
        print f.func_name, args, kwargs
        return f(*args, **kwargs)
    return decorated

@decorator
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'herobase/profile.html', {
        'user': user
    })

@login_required
def profile_edit(request):
    user = request.user
    form = UserProfileEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile successfully changed')
    return render(request, 'herobase/profile_edit.html', {
        'user': user,
        'form': form
    })



