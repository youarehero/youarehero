# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from herobase.models import Adventure
from heronotification import notify

logger = logging.getLogger(__name__)

# for each hero: how can the owner interact with the hero? (accept/refuse)

# {% for adventure in adventures %}
# {% endfor %}

# owner hero management
def owner_hero_accept(quest, hero):
    if not quest.open:
        raise ValidationError("Can't accept heroes into a quest that isn't open.")

    try:
        adventure = quest.adventures.get(user=hero, rejected=False, accepted=False)
    except Adventure.DoesNotExist:
        raise ValidationError("Can't accept a hero who is not applying.")

    adventure.accepted = True
    adventure.save()

    # update open state
    quest.save()
    notify.hero_accepted(adventure.user, quest)

    return _("You have accepted %s." % hero.username)

def owner_hero_reject(quest, hero):
    if not quest.open:
        raise ValidationError("Can't reject heroes when a quest isn't open.")

    try:
        adventure = quest.adventures.get(user=hero, accepted=False, rejected=False)
    except Adventure.DoesNotExist:
        raise ValidationError("Can't reject a hero who is not applying.")

    adventure.rejected = True
    adventure.save()
    quest.save()

    notify.hero_rejected(adventure.user, quest)
    return _("You have rejected %s." % hero.username)


# owner quest management
def owner_quest_start(quest, message_for_heroes):
    pass

def owner_quest_cancel(quest):
    if quest.canceled or quest.done:
        raise ValidationError("Can not cancel when already done/canceled.")

    quest.canceled = True
    quest.save()

    for hero in quest.heroes.filter(canceled=False):
        notify.quest_cancelled(hero, quest)

def owner_quest_done(quest):
    if quest.canceled or quest.done:
        raise ValidationError("Can not cancel when already done/canceled.")
    if not quest.accepted_heroes():
        raise ValidationError("A quest without accepted heroes can't be marked as done.")
    quest.done = True
    quest.save()

    for hero in quest.heroes.filter(canceled=False, accepted=True):
        notify.quest_done(hero, quest)


# hero participation
def hero_quest_apply(quest, hero):
    if not quest.open:
        raise ValidationError("Can not apply for a quest that isn't open.")

    if quest.adventures.filter(user=hero, canceled=False).exists():
        raise ValidationError("Can only apply once.")

    if quest.adventures.filter(user=hero, accepted=True).exists():
        raise ValidationError("Can not apply after being accepted.")

    adventure, created = quest.adventures.get_or_create(user=hero)
    if adventure.canceled:
        adventure.canceled = False
        adventure.canceled_time = None
        adventure.save()
    quest.save()

    notify.hero_has_applied(quest.owner, adventure)


def hero_quest_done(quest, hero):
    pass

def hero_quest_cancel(quest, hero):
    if not quest.open or quest.canceled or quest.done:
        raise ValidationError("You can't cancel participation at this time.")

    if quest.adventures.filter(user=hero, canceled=True).exists():
        raise ValidationError("You can't cancel multiple times.")

    if not quest.adventures.filter(user=hero).exists():
        raise ValidationError("You need to apply before cancelling.")

    adventure = quest.adventures.get(user=hero)
    adventure.canceled = True
    adventure.save()
    quest.save()

    notify.hero_has_cancelled(quest.owner, adventure)