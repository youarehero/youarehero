# -*- coding: utf-8 -*-
import logging
from django.http import Http404, HttpResponse
from django.template import Template
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)



from debug_toolbar.panels import DebugPanel
from django.core import mail


class MailDebugPanel(DebugPanel):
    """
    Panel that displays emails from the locmem email backend.
    """
    name = 'Mails'
    template = "mail_debug_panel/debug_toolbar_message.html"
    has_content = True

    def __init__(self, *args, **kwargs):
        super(MailDebugPanel, self).__init__(*args, **kwargs)

    def nav_title(self):
        return 'Mails (%d)' % self._length

    def title(self):
        return 'Mails (%d)' % self._length

    def url(self):
        return ''

    def process_response(self, request, response):
        queued_messages = getattr(mail, 'outbox', [])
        self._length = len(queued_messages)

        messages = []
        while queued_messages:
            messages.append(queued_messages.pop())

        self.record_stats({
            'messages': messages
        })