# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from herobase.forms import UserAuthenticationForm
from herobase.models import Quest
from django.utils.translation import ugettext as _

def login_form(request):
    """Add login_form to template context if the user is not authenticated."""
    if request.user.is_anonymous():
        return {'login_form': UserAuthenticationForm(request)}
    return {}



def butler_text(request):
    active = lambda *args, **kwargs: reverse(*args, **kwargs) == request.path
    below = lambda *args, **kwargs: request.path.startswith(reverse(*args, **kwargs))
    if not request.user.is_anonymous:
        profile = request.user.get_profile()
    text = _(u'Do you want to spite me %%%salutation%%%?')
    if active('home'):
        text = _(u'Good day %%%salutation%%%,\nas soon as you have posted or accepted your first quests, the main page will provide you with a list of notifications about your recent activities and everything new that has happened in the past days.\n\nIf you wish, you can also be informed about status modifications in your quests and respectively about new messages.\n\nThis can be turned on and off as requested in your settings (the symbol with the cog).')
    if active('quest_list'):
        text = _(u'This is the pinnboard %%%salutation%%%.\nHere you can find all available quests. Should you feel overwhelmed by the choice, you can use the searchbar to narrow down the choice via keywords or via different criteria such as time exposure or the necessity to do the quest.\nlocally.Visiting the pinnboard frequently will be worth your while - if I may say so.\n%%%salutation%%%.')
    if active('quest_create'):
        text =_(u'Here you can find all the forms you need, %%%salutation%%%.\nPosting a new quest for the world to solve or offering a new project, you´ll be not lacking the forms to do so.')
    if active('quest_my'):
        text =_(u'Here you can see all quests that you have accepted and posted %%%salutation%%%.\n If there is a star mark it means that you are the quest provider.')
    #if active('quest_my_created'):
    #    text ='Hier finden Sie alle Quests die Sie aufgegeben haben %%%salutation%%%.\n'
    #if active('quest_my_joined'):
    #    text ='Hier finden Sie alle Quests die Sie angenommen haben %%%salutation%%%.\n'
    #if active('quest_my_done'):
    #    text ='Hier finden Sie alle Quests die Sie bereits erledigt haben %%%salutation%%%.\n '
    if not request.user.is_anonymous and profile.sex==1:
        text=text.replace("%%%salutation%%%","Sir")
    else:
        if not request.user.is_anonymous and profile.sex==2:
            text=text.replace("%%%salutation%%%","Madam")
        else:
            text=text.replace("%%%salutation%%%","")
    return {'butler_default_text': text}
