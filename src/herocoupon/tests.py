# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest
from herocoupon.models import Coupon


class CouponTest(WebTest):
    def test_coupon_code_generation(self):
        coupon = G(Coupon, type='single', xp=31563, is_active=True,
                   code='', redeemed_by=[])
        self.assertEqual(len(coupon.code), 10)

    def test_invalid_coupon(self):
        user = G(User, username='ahero')
        code = 'LH5SNU89SO'

        redeem_page = self.app.get(reverse('redeem', kwargs={'code': code}),
                                   user=user)
        redeem_page.mustcontain(u'Ungültig')

    def test_deactivated_coupon(self):
        user = G(User, username='ahero')
        coupon = G(Coupon, type='single', xp=31563, is_active=False,
                   code='', redeemed_by=[])

        redeem_page = self.app.get(reverse('redeem', kwargs={'code': coupon.code}),
                                   user=user)
        redeem_page.mustcontain(u'Deaktiviert', coupon.code)

    def test_single_coupon(self):
        user = G(User, username='ahero')
        coupon = G(Coupon, type='single', xp=31563, is_active=True,
                   code='', redeemed_by=[])

        redeem_page = self.app.get(reverse('redeem', kwargs={'code': coupon.code}),
                                   user=user)
        user = User.objects.get(username=user.username)
        coupon = Coupon.objects.get(code=coupon.code)

        redeem_page.mustcontain(u'Herzlichen Glückwunsch', coupon.code,
                                unicode(coupon.xp))
        self.assertEqual(user.profile.experience, coupon.xp)
        self.assertIn(user, coupon.redeemed_by.all())
        self.assertEqual(coupon.is_active, False)

    def test_multi_coupon(self):
        user = G(User, username='ahero')
        coupon = G(Coupon, type='multi', xp=31563, is_active=True,
                   code='', redeemed_by=[])

        redeem_page = self.app.get(reverse('redeem', kwargs={'code': coupon.code}),
                                   user=user)
        user = User.objects.get(username=user.username)
        coupon = Coupon.objects.get(code=coupon.code)

        redeem_page.mustcontain(u'Herzlichen Glückwunsch', coupon.code,
                                unicode(coupon.xp))
        self.assertEqual(user.profile.experience, coupon.xp)
        self.assertIn(user, coupon.redeemed_by.all())
        self.assertEqual(coupon.is_active, True)

    def test_multi_coupon_already_used(self):
        user = G(User, username='ahero')
        coupon = G(Coupon, type='multi', xp=31563, is_active=True,
                   code='', redeemed_by=[user])

        redeem_page = self.app.get(reverse('redeem', kwargs={'code': coupon.code}),
                                   user=user)
        redeem_page.mustcontain(u'Bereits verwendet', coupon.code)