# Create your views here.
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from herobase.forms import QuestCreateForm
from herobase.models import Quest, Adventure


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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class QuestDetailView(DetailView):
    context_object_name = "quest"
    model = Quest

    def get_template_names(self):
        if self.object.author == self.request.user:
            return ['herobase/quest/detail_for_author.html']
        else:
            return ['herobase/quest/detail_for_hero.html']

def home_view(request):
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {'open_quests': Quest.objects.filter(state=Quest.STATE_OPEN)})


def hero_home_view(request):
    hero = request.user
    return render(request, 'herobase/hero_home.html',
            {'hero': hero,
             'profile': hero.get_profile(),
             'adventures': hero.adventures.order_by('-created'),
             'authored_quests': hero.authored_quests.order_by('-created')})


@require_http_methods(["POST"])
@login_required
def adventure_update(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    if quest.author == request.user:
        messages.error(request, 'You are the author.')
        return render(request, 'herobase/quest/detail_for_author.html', {'quest': quest})
    elif request.user in User.objects.filter(quests=quest):
        messages.info(request, 'You are already applying for the quest "%s".' % quest.title)
        return render(request, 'herobase/quest/detail_for_hero.html', {'quest': quest})
    else: #hero not assigned yet
        adventure = Adventure.objects.create(user=request.user, quest=quest, state=Adventure.STATE_APPLIED)
        adventure.save()
        messages.success(request, 'You are a hero!')
    return render(request, 'herobase/quest/adventure_update.html', {'quest': quest})
