from django.contrib import admin
from django.core.urlresolvers import reverse
from herocoupon.models import Coupon

class CouponAdmin(admin.ModelAdmin):
    def coupon_url(self, coupon):
        path = reverse('redeem', kwargs={'code': coupon.code})
        return '%s%s' % ( "https://youarehero.net", path)
    coupon_url.short_description = 'URL'

    list_display = ('code', 'coupon_url', 'type', 'xp', 'is_active')

admin.site.register(Coupon, CouponAdmin)
