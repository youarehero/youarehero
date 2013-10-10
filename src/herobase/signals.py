# -*- coding: utf-8 -*-
from django.dispatch import Signal

quest_done = Signal(providing_args=["quest"])