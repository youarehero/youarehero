# -*- coding: utf-8 -*-
'''
This module provides a custom Model-Action functionality.
Model-Actions are methods on models (decorated with @action), which changes
the model states in a defined way.
'''
from django.core.exceptions import PermissionDenied
from django.utils.datastructures import SortedDict
from django.utils.decorators import method_decorator

def action(verbose_name=None, condition=None):
    index = getattr(action, 'index', 1)
    def decorator(f):
        f.action = index
        f.verbose_name = verbose_name or f.__name__
        return f
    setattr(action, 'index', index + 1)
    return method_decorator(decorator)

class ActionMixin(object):
    """Provides a mixin to use in Models that want to implement actions."""

    def get_actions(self):
        """
        Return a list of actions representing available actions for a model
        instance.
        """
        if not hasattr(self.__class__, '_cached_actions'):
            actions = []
            for key, element in self.__class__.__dict__.items():
                if getattr(element, 'action', None):
                    actions.append((key, element))
            actions.sort(key=lambda (key, element): element.action)
            setattr(self.__class__, '_cached_actions', zip(*actions)[0])
        return getattr(self.__class__, '_cached_actions')

    def valid_actions_for(self, request):
        """
        Return a dict containing all actions that may be executed given a
        request.
        """
        actions = self.get_actions()
        valid_actions = SortedDict()
        for name in actions:
            action = getattr(self, name)
            if action(request, validate_only=True):
                valid_actions[name] = {'verbose_name': action.verbose_name}
        return valid_actions

    def process_action(self, request, action_name):
        """Execute an action if all its preconditions are satisfied."""
        actions = self.get_actions()
        if not action_name in actions:
            raise ValueError("not a valid action")
        action = getattr(self, action_name)
        if not action(request, validate_only=True):
            raise PermissionDenied(action_name)
        return action(request)
