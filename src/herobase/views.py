# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from herobase.forms import QuestCreateForm
from herobase.models import Quest


class QuestListView(ListView):
    context_object_name = "quests"
    queryset = Quest.objects.filter(state=Quest.STATE_OPEN)
    template_name = "herobase/quest_list.html"



class QuestCreateView(CreateView):
    context_object_name = "quest"
    form_class = QuestCreateForm
    template_name = "herobase/quest_create.html"
    success_url = './%(id)s'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class QuestDetailView(DetailView):
    context_object_name = "quest"
    model = Quest
    template_name = "herobase/quest_detail.html"


#class QuestUpdateView(UpdateView):
