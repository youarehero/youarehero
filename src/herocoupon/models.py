from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.utils.translation import ugettext as _
import random


class Coupon(models.Model):
    TYPE_CHOICES = (
        ('single', _(u'Single')),
        ('multi', _(u'multi')),
    )
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='single')
    xp = models.PositiveSmallIntegerField(default=0)
    code = models.CharField(max_length=255, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    redeemed_by = models.ManyToManyField(User)

    @classmethod
    def generate_code(cls):
        chars = 'ABCDEFGHKMNPQRSTWXYZ23456789' # whitout IJ O0 l1 UV
        code = ''.join([random.choice(chars) for _ in range(10)])
        if Coupon.objects.filter(code=code).exists():
            return cls.generate_code()
        return code

    def clean(self):
        # prevent empty custom-id from unique checks
        if not self.code or self.code.strip() == '':
            self.code = self.generate_code()

        super(Coupon, self).clean()
        errors = []
        # validation checks here
        if len(errors) > 0:
            raise ValidationError(errors)

    def __unicode__(self):
        return u'%s%s%s' % (self.code, self.type, self.xp)