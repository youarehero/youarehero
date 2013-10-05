# -*- coding: utf-8 -*-
from django.contrib import admin
import logging

from .models import Organization

logger = logging.getLogger(__name__)


admin.site.register(Organization)