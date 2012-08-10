# -*- coding: utf-8 -*-
"""
The Views module provide view functions, which were called by the
`url dispatcher <https://docs.djangoproject.com/en/1.4/topics/http/urls/>`_,
and aggregate some data for use in templates.
"""
from datetime import datetime
from itertools import chain
from django.contrib.auth.models import User
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.signing import Signer
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.contrib import messages
from utils import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator

from django.views.generic.edit import CreateView
from filters import QuestFilter
from herobase.forms import QuestCreateForm, UserProfileEdit, UserProfilePrivacyEdit
from herobase.models import Quest, Adventure, CLASS_CHOICES, UserProfile
import logging
from django.db.models import Count, Sum

logger = logging.getLogger('youarehero.herobase')

@login_required
def quest_list_view(request, template='herobase/quest/list.html'):
    """Basic quest list, with django-filter app"""
    f = QuestFilter(request.GET, queryset=Quest.objects.order_by('-created'))
    return render(request, template, {
        'filter': f,
        'quests': f.qs,
    })

class QuestCreateView(CreateView):
    """Basic Quest create view. This generic view-class should be refactored to a normal view function"""
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


def quest_detail_view(request, quest_id, template="herobase/quest/detail.html"):
    """Render detail template for quest, and adventure if it exists."""
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
    return render(request, template, context)

def home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {
        'open_quests': Quest.objects.filter(state=Quest.STATE_OPEN)})


def m_home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    return hero_home_view(request, template='herobase/m/home.html')
#    return render(request, "herobase/m/public_home.html", {'open_quests':
#        Quest.objects.filter(state=Quest.STATE_OPEN)})

def abstract(request):
    """static you are hero abstract view."""
    return render(request, "herobase/abstract.html")

def hero_classes(request):
    """static view for explaining hero classes."""
    return render(request, "herobase/hero_classes.html")

@login_required
def hero_home_view(request, template='herobase/hero_home.html'):
    """the hero home is only visible for authenticated heros."""
    user = request.user
    return render(request, template,
            {
             #'profile': user.get_profile(),
             'quests_active': user.created_quests.active().order_by('-created'),
             'quests_old': user.created_quests.inactive().order_by('-created'),
             'quests_joined': Quest.objects.active().filter(adventure__user=user).exclude(adventure__user=user, adventure__state=Adventure.STATE_HERO_CANCELED)
             })


@login_required
def quest_my(request, template='herobase/quest/my.html'):
    """Views the quests the hero is envolved with."""
    user = request.user
    return render(request, template,
            {
            #'profile': user.get_profile(),
            'quests_active': user.created_quests.active().order_by('-created'),
            'quests_old': user.created_quests.inactive().order_by('-created'),
            'quests_joined': Quest.objects.active().filter(adventure__user=user).exclude(adventure__user=user, adventure__state=Adventure.STATE_HERO_CANCELED)
        })

@require_POST
@login_required
def quest_update(request, quest_id):
    """Handle POST data for quest-actions and redirect to quest-detail-view."""
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
    """Handle POST data for adventure-actions and redirect to quest-detail-view."""
    quest = get_object_or_404(Quest, pk=quest_id)

    adventure_id = request.POST.get('adventure_id')
    adventure = get_object_or_404(quest.adventure_set, pk=adventure_id)

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
def userprofile(request, username=None, template='herobase/userprofile/detail.html'):
    """Render Userprofile with some stats."""
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


    return render(request, template, {
        'user': user,
        'rank': rank,
        'colors': mark_safe(simplejson.dumps(colors)),
        'completed_quest_count': user.adventures.filter(state=Adventure.STATE_OWNER_DONE).count(),
        'hero_completed_quests': mark_safe(simplejson.dumps(hero_completed_quests)),
    })


@login_required
def userprofile_edit(request):
    """Render the userprofile form and handle possible changes."""
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
    """Render another userprofile form for privacy settings saved on the userprofile."""
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
    """Render a view of the top heroes by rank."""
    top_creators = User.objects.filter(created_quests__state=Quest.STATE_OWNER_DONE).annotate(quest_count=Count('created_quests')).filter(quest_count__gt=0).order_by('-quest_count')
    local = None
    if request.user.is_authenticated():
        total, local = request.user.get_profile().get_related_leaderboard()
    else:
        total = User.objects.select_related().filter(userprofile__experience__gt=0).order_by('-userprofile__experience')

    return render(request, "herobase/leader_board.html", {'total': total,
                                                          'local': local,
                                                         'top_creators': top_creators,
                                                         'myname': request.user.username
                                                         })
@login_required
def random_stats(request):
    """Some general stats"""
    user = request.user
    class_choices = dict(CLASS_CHOICES)
    color_dict = { None: "#ff0000",
                    5: '#e8e8e8',
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
        hero_completed_quests.append((class_choices.get(choice), count))

    colors0 = []
    open_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OPEN).values_list('hero_class').annotate(Count('hero_class')):
        open_quest_types.append((class_choices.get(choice), count))
        colors0.append(color_dict[choice])

    colors1 = []
    completed_quest_types = []
    for choice, count in  Quest.objects.filter(state=Quest.STATE_OWNER_DONE).values_list('hero_class').annotate(Count('hero_class')):
        completed_quest_types.append((class_choices.get(choice) , count))
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
    """Special view for nosy developers."""
    if request.user.is_authenticated() and request.user.is_staff:
        logged_in = '\n'.join('%s: %s' % (u.last_login, u.username) for u in User.objects.order_by('-last_login')[:20])
        signed_up = '\n'.join('%s: %s' % (u.date_joined, u.username) for u in User.objects.order_by('-date_joined')[:10])
        return HttpResponse('Logged in \n%s\nJoined\n%s' % (logged_in, signed_up), mimetype='text/plain')
    else:
        raise Http404()





def send_keep_account_mails():
    return # TODO : test this, correct text, send mails
    users = User.objects.filter(username='raphael')
    mail_template = """\
Liebe Heldinnen, liebe Helden

Erstmal vielen Dank für das Erstellen eures Accounts und die Teilnahme
an dem Playtest bei der GPN.
Wir haben sehr viel Feedback bekommen und viele gute Anregungen für
die Weiterentwicklung der Plattform.


Wenn ihr weiter über YAH auf dem Laufenden gehalten werden wollt,
 dann klickt bitte auf den Bestätigungslink.

{url}

Alle Accounts die nicht innerhalb der nächsten Woche bestätigen
werden wir wie angekündigt löschen.


VIELEN DANK FÜRS MITMACHEN und viel Spass bei all euren zukünftigen
Heldentaten - ob nun mit Plattform oder ohne :)

YAH!!!
"""

    signer = Signer(salt='keep-email')
    for user in users:
        email = signer.sign(user.email)
        relative_url = reverse('keep-email', args=(email,))
        url = 'https://youarehero.net%s' % relative_url

        mail_text = mail_template.format(url=url)
        send_mail("You Are Hero", mail_text, from_email='noreply@youarehero.net', recipient_list=[user.email])


def confirm_keep_email(request, action):
    signer = Signer(salt='keep-email')
    try:
        email = signer.unsign(action)
    except signing.BadSignature:
        return HttpResponse("I'm afraid i can't do that dave.", mimetype='text/plain')

    user = User.objects.get(email=email)
    profile = user.get_profile()

    if profile.keep_email_after_gpn:
        return HttpResponse("Already keeping email for %s" % email, mimetype='text/plain')
    else:
        profile.keep_email_after_gpn = datetime.now()
        profile.save()
        return HttpResponse("Keeping email for %s" % email, mimetype='text/plain')



