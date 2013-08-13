from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from datetime import timedelta, datetime
from herobase.models import Quest
from django.contrib.comments import Comment
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    args = '<timestamp>'
    help = 'Sends mails to ADMIN with all new/modified ' +\
        'quests and comments since <timestamp> (defaults to 1 day ago)'

    def handle(self, *args, **options):
        if len(args) > 0:
            since = datetime.utcfromtimestamp(int(args[0]))
        else:
            since = datetime.now() - timedelta(days=1)

        self.stdout.write(u"Sending out posts since {0}\n".format(since))

        quests = Quest.objects.filter(modified__gte=since)

        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(Quest),
            submit_date__gte=since
        )

        if len(quests) == 0 and len(comments) == 0:
            self.stdout.write("Nothing new to report")
            return

        text = u""
        for quest in quests:
            text += u"=== Modified/New Quest #{0}: {1}\n{2}\n\n"\
                    .format(quest.pk, quest.title, quest.description)

        for comment in comments:
            text += u"=== Modified/New comment #{0}:\n{1}\n\n"\
                    .format(comment.pk, comment.comment)

        send_mail(
            u"YAH Admin Digest",
            text,
            u"digest@youarehero.net",
            [addr for (_, addr) in settings.ADMINS]
        )
