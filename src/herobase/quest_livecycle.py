# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext as _


class LazyNotifier(object):
    def __getattr__(self, item):
        from heronotification import notify
        return getattr(notify, item)
notify = LazyNotifier()


logger = logging.getLogger(__name__)


def there_are_no(f):
    def decorated(*args, **kwargs):
        exception = kwargs.get('exception', False)
        result = f(*args, **kwargs)
        if exception and result is not None:
            raise ValueError(result)
        else:
            return not result
    return decorated


class State(object):
    @staticmethod
    def assert_no(errors):
        if errors is not None:
            raise ValidationError(errors)


class QuestState(State):
    def __init__(self, quest):
        self.quest = quest

    def accept_all_errors(self):
        if not self.quest.open:
            return "Can't accept all if quest not open."
    can_accept_all = there_are_no(accept_all_errors)

    def accept_all(self):
        self.assert_no(self.accept_all_errors())

        for adventure in self.quest.adventures.pending():
            adventure.state.accept()

    def start_errors(self):
        if self.quest.adventures.accepted().count() < self.quest.min_heroes:
            return "Can't start quest if there aren't enough heroes."
        if self.quest.canceled:
            return "Can't start a canceled quest."
        if self.quest.done:
            return "Can't start a done quest."
    can_start = there_are_no(start_errors)

    def start(self):  # <-  quest
        self.assert_no(self.start_errors())

        self.quest.started = True
        self.quest.save()

        for adventure in self.quest.adventures.accepted():
            notify.quest_started(adventure.user, self.quest)

    def cancel_errors(self):
        if self.quest.canceled:
            return "Can't cancel a canceled quest."
        if self.quest.done:
            return "Can't cancel a done quest."
    can_cancel = there_are_no(cancel_errors)

    def cancel(self):
        self.assert_no(self.cancel_errors())

        self.quest.canceled = True
        self.quest.save()

        for adventure in self.quest.adventures.accepted():
            notify.quest_cancelled(adventure.user, self.quest)

    def done_errors(self):
        if not self.quest.started:
            return "Can't mark a quest as done that isn't started."

        if self.quest.canceled:
            return "Can't mark a canceled quest as done."

        if self.quest.done:
            return "Can't mark a done quest as done."
    can_done = there_are_no(done_errors)

    def done(self):
        self.assert_no(self.done_errors())
        from herobase.models import QUEST_EXPERIENCE

        self.quest.done = True
        self.quest.save()

        self.quest.owner.get_profile().experience += QUEST_EXPERIENCE
        self.quest.owner.get_profile().save()

        for adventure in self.quest.adventures.accepted():
            notify.quest_done(adventure.user, self.quest)
            adventure.user.get_profile().experience += QUEST_EXPERIENCE
            adventure.user.get_profile().save()


class AdventureState(State):
    def __init__(self, quest, hero, adventure=None):
        self.quest = quest
        self.hero = hero
        self._adventure = adventure

    @property
    def adventure(self):
        if self._adventure is None:
            self._adventure = self.quest.adventures.pending().get(user=self.hero)
        return self._adventure

    def accept_errors(self):
        if not self.quest.open:
            return "Can't accept heroes into a quest that isn't open."
        if not self.quest.adventures.pending().filter(user=self.hero).exists():
            return "Can't accept a hero who is not applying."
    can_accept = there_are_no(accept_errors)

    def accept(self):
        self.assert_no(self.accept_errors())

        self.adventure.accepted = True
        self.adventure.save()

        # update open state
        self.quest.save()
        notify.hero_accepted(self.adventure.user, self.quest)

        return _("You have accepted %s." % self.hero.username)

    def apply_errors(self):
        if not self.quest.open:
            return "Can not apply for a quest that isn't open."
        if self.quest.adventures.filter(user=self.hero, canceled=False).exists():
            return "Can only apply once."
        if self.quest.adventures.filter(user=self.hero, accepted=True, canceled=False).exists():
            return "Can not apply after being accepted."
        if not self.quest.owner.trusted and not self.hero.profile.is_legal_adult():
            return "Minors cannot apply for untrusted users' quests"
    can_apply = there_are_no(apply_errors)

    def apply(self):
        self._adventure, created = self.quest.adventures.get_or_create(user=self.hero)
        from herobase.models import APPLY_EXPERIENCE

        # only gives experience when applying the first time
        if created:
            self.hero.get_profile().experience += APPLY_EXPERIENCE
            self.hero.get_profile().save()

        # reset cancel if cancelled
        if self.adventure.canceled:
            self.adventure.canceled = False
            self.adventure.canceled_time = None
            self.adventure.save()

        if self.quest.auto_accept:
            self.adventure.accepted = True
            self.adventure.accepted_time = datetime.now()
            self.adventure.save()
            notify.hero_accepted(self.hero, self.quest)
        else:
            notify.hero_has_joined(self.quest.owner, self.adventure)

    def reject_errors(self):
        if not self.quest.open:
            return "Can't reject heroes when a quest isn't open."
        if not self.quest.adventures.filter(user=self.hero, accepted=False, rejected=False,
                                         canceled=False).exists():
            return "Can't reject a hero who is not applying."
    can_reject = there_are_no(reject_errors)

    def reject(self):
        self.assert_no(self.reject_errors())
        self.adventure.rejected = True
        self.adventure.save()
        self.quest.save()

        notify.hero_rejected(self.adventure.user, self.quest)
        return _("You have rejected %s." % self.hero.username)

    def cancel_errors(self):
        if self.quest.started or self.quest.canceled or self.quest.done:
            return "You can't cancel participation at this time."
        if self.quest.adventures.filter(user=self.hero, canceled=True).exists():
            return "You can't cancel multiple times."
        if not self.quest.adventures.filter(user=self.hero).exists():
            return "You need to apply before cancelling."
    can_cancel = there_are_no(cancel_errors)

    def cancel(self):
        self.assert_no(self.cancel_errors())

        self.adventure.canceled = True
        self.adventure.save()
        self.quest.save()

        notify.hero_has_cancelled(self.quest.owner, self.adventure)
