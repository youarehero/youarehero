# -*- coding: utf-8 -*-
"""
The Views module provide view functions, which were called by the
`url dispatcher <https://docs.djangoproject.com/en/1.4/topics/http/urls/>`_,
and aggregate some data for use in templates.
"""
from datetime import datetime
from itertools import chain
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.core.signing import Signer
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.contrib import messages
from herobase import quest_livecycle
from heronotification.models import Notification
from herorecommend import recommend_for_user, recommend, recommend_local
from herorecommend.forms import UserSkillEditForm
from utils import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.views.generic.edit import CreateView
from filters import QuestFilter
from herobase.forms import QuestCreateForm, UserProfileEdit, UserProfilePrivacyEdit
from herobase.models import Quest, Adventure, CLASS_CHOICES, UserProfile
import logging
from django.db.models import Count, Sum
import herorecommend.signals as recommender_signals 
from herorecommend.models import MIN_SELECTED_SKILLS
logger = logging.getLogger('youarehero.herobase')

@login_required
def quest_list_view(request, template='herobase/quest/list.html'):
    """Basic quest list, with django-filter app"""
    if request.user.is_authenticated():
        f = QuestFilter(request.GET, queryset=recommend(request.user, order_by=['-created']))
    else:
        f = QuestFilter(request.GET, queryset=Quest.objects.filter(open=True).order_by('-created'))
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


def quest_detail_view(request, quest_id):
    """Render detail template for quest, and adventure if it exists."""
    quest = get_object_or_404(Quest, pk=quest_id)

    context = {
        'quest': quest,
        'is_owner': request.user == quest.owner
    }
    if request.user.is_authenticated():
        try:
            context['adventure'] = quest.adventures.get(user_id=request.user.pk, canceled=False)
        except Adventure.DoesNotExist:
            pass

    return render(request, "herobase/quest/detail.html", context)

def home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {
        'open_quests': Quest.objects.filter(open=True)})


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
             'notifications': Notification.objects.filter(user=user).order_by('-read', '-created'),
#             'quests_active': user.created_quests.filter(canceled=False, done=False).order_by('-created')[:10],
#             'quests_old': user.created_quests.filter(done=True).order_by('-created')[:10],
#             'quests_joined': Quest.objects.filter(canceled=False, adventures__user=user, adventures__canceled=False)[:10]
             })


@login_required
def quest_my(request, template='herobase/quest/my.html'):
    """Views the quests the hero is envolved with."""
    user = request.user
    return render(request, template,
            {
            #'profile': user.get_profile(),
            'quests_active': user.created_quests.filter(canceled=False, done=False).order_by('-created')[:10],
            'quests_old': user.created_quests.exclude(canceled=False, done=False).order_by('-created')[:10],
            'quests_joined': Quest.objects.filter(canceled=False, done=False).filter(adventures__user=user)[:10]
        })

@require_POST
@login_required
def owner_update_quest(request, quest_id):
    """Handle POST data for quest-actions and redirect to quest-detail-view."""
    quest = get_object_or_404(Quest, pk=quest_id)
    if not quest.owner == request.user:
        return HttpResponseForbidden("You are not the owner of this quest.")

    # start / cancel / done / document

    action = request.POST.get('action')
    if action == 'start':
        message_for_heroes = request.POST.get('message_for_heroes')
        quest_livecycle.owner_quest_start(quest, message_for_heroes)
    elif action == 'cancel':
        quest_livecycle.owner_quest_cancel(quest)
    elif action == 'done':
        quest_livecycle.owner_quest_done(quest)
    else:
        raise ValidationError('No known action specified')
    return HttpResponseRedirect(reverse('quest-detail', args=(quest.pk, )))

@require_POST
@login_required
def owner_update_hero(request, quest_id, hero_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    hero = get_object_or_404(User, pk=hero_id)

    if not quest.owner == request.user:
        return HttpResponseForbidden("You are not the owner of this quest.")

    action = request.POST.get('action')
    if action == 'accept':
        quest_livecycle.owner_hero_accept(quest, hero)
    elif action == 'reject':
        quest_livecycle.owner_hero_reject(quest, hero)
    else:
        raise ValidationError('No known action specified')

    return HttpResponseRedirect(reverse('quest-detail', args=(quest.pk, )))

@require_POST
@login_required
def hero_update_quest(request, quest_id):
    """Handle POST data for adventure-actions and redirect to quest-detail-view."""
    quest = get_object_or_404(Quest, pk=quest_id)

    if quest.owner == request.user:
        raise ValidationError("Im afraid I can't let you do that.")

    action = request.POST.get('action')
    if action == 'apply':
        quest_livecycle.hero_quest_apply(quest, request.user)
    elif action == 'cancel':
        quest_livecycle.hero_quest_cancel(quest, request.user)
    else:
        raise ValidationError('No known action specified')
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
            .filter(done=True)\
            .values_list('quest__hero_class')\
            .annotate(Count('quest__hero_class')):
        colors.append(color_dict[choice])
        hero_completed_quests.append((class_choices[choice], count))


    return render(request, template, {
        'user': user,
        'rank': rank,
        'colors': mark_safe(json.dumps(colors)),
        'completed_quest_count': user.adventures.filter(done=True).count(),
        'hero_completed_quests': mark_safe(json.dumps(hero_completed_quests)),
    })


@login_required
def userprofile_edit(request):
    """Render the userprofile form and handle possible changes."""
    user = request.user
    form = UserProfileEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile successfully changed')
        return HttpResponseRedirect(reverse("userprofile-edit"))
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
def userprofile_skill_settings(request):
    form = UserSkillEditForm(request.POST or None, instance=request.user.selected_skills)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('.')

    context = { 'selected': len(request.user.selected_skills.get_skills()),
                'minimum': MIN_SELECTED_SKILLS,
                'form': form,
            }
    return render(request, 'herobase/userprofile/skill_settings.html', context)

@login_required
def leader_board(request):
    """Render a view of the top heroes by rank."""
    top_creators = User.objects.filter(created_quests__state=Quest.STATE_OWNER_DONE).annotate(quest_count=Count('created_quests')).filter(quest_count__gt=0).order_by('-quest_count')

    if request.user.is_authenticated():
        global_board = request.user.get_profile().get_local_relative_leaderboard()
        local_board = request.user.get_profile().get_local_relative_leaderboard()
    else:
        global_board = User.objects.select_related().filter(userprofile__experience__gt=0).order_by('-userprofile__experience')
        local_board = None

    return render(request, "herobase/leader_board.html", {
        'global_board': global_board,
        'local_board': local_board,
        'top_creators': top_creators,
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
        .filter(quest__done=True)\
        .filter(done=True)\
        .values_list('quest__hero_class')\
        .annotate(Count('quest__hero_class')):
        hero_completed_quests.append((class_choices.get(choice), count))

    colors0 = []
    open_quest_types = []
    for choice, count in  Quest.objects.filter(open=True).values_list('hero_class').annotate(Count('hero_class')):
        open_quest_types.append((class_choices.get(choice), count))
        colors0.append(color_dict[choice])

    colors1 = []
    completed_quest_types = []
    for choice, count in  Quest.objects.filter(open=True).values_list('hero_class').annotate(Count('hero_class')):
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
        context[key] = mark_safe(json.dumps(list(context[key])))

    context.update({
        'quests_completed': user.adventures.filter(quest__done=True).count()
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

@require_POST
@login_required
def like_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    like, created = Like.objects.get_or_create(user=request.user, quest=quest)

    if created:
        recommender_signals.like.send(sender=request.user, quest=quest) 

    return HttpResponse(json.dumps({'success': True}), mimetype='application/json')
