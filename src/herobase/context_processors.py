# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from herobase.forms import UserAuthenticationForm
from herobase.models import Quest

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
    text = 'Wollen Sie mich ärgern %%%salutation%%%?'
    if active('home'):
        text = 'Guten Tag %%%salutation%%%,\nsobald Sie Ihre ersten Quests eingestellt bzw. angenommen haben, werden Sie hier auf der Startseite eine Übersicht dessen sehen, was für Sie ansteht; bzw. was sich in den letzten Tagen Neues ereignet hat.\n\nWenn Sie es wünschen können Sie auch per email über Statusänderungen in Ihren Quests bzw. über neue Nachrichten informiert werden.\n\nDies können Sie nach Wunsch in den Optionen (das Symbol mit den Zahnrädern) einstellen.'
    if active('quest_list'):
        text = 'Sie befinden sich auf der Pinnwand %%%salutation%%%.\nHier finden Sie alle Quests, derer Sie sich annehmen können. Falls Sie von der Auswahl überwältigt sein sollten, können Sie mit Hilfe der Suchkriterien Ihre Auswahl einschränken.\nSo gibt es die Möglichkeit nach Stichworten suchen um etwas zu finden, das zu Ihnen passt oder auf das Sie gerade Lust haben.\n\nAuch bestimmte Kriterien wie der geschätzte Zeitaufwand oder ob Sie für die Quest lokal anwesend sein müssen, sollen es Ihnen erleichtern, eine Auswahl zu treffen.\n\\”Frenquentierte Besuche lohnen sich, wenn ich das so sagen darf %%%salutation%%%.'
    if active('quest_create'):
        text ='Hier finden Sie alle Formulare, die Sie brauchen %%%salutation%%%.\nOb Sie der Welt eine weitere Aufgabe zum Lösen bieten oder ein neues Projekt einstellen wollen, ich habe die Formulare für Sie vorbereitet.'
    if active('quest_my'):
        text ='Hier finden Sie alle Quests die Sie angenommen oder aufgegeben haben %%%salutation%%%.\n Wenn ein Stern an der Quest ist bedeutet das das es sich um eine von ihnen aufgegeben Quest handelt.'
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