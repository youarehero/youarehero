# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from herocoupon.models import Coupon

@login_required
def redeem_coupon(request, code):
    coupons = Coupon.objects.filter(code=code)

    if not coupons.exists():
        return render(request, "herocoupon/not_found.html", {'code': code})
    coupon = coupons[0]
    if not coupon.is_active:
        return render(request, "herocoupon/not_active.html", {'code': code})
    if request.user in coupon.redeemed_by.all():
        return render(request, "herocoupon/already_used.html", {'code': code})

    # The Couppon exists, is active and not already redeemed by the user
    profile = request.user.profile
    profile.experience += coupon.xp
    profile.save()

    coupon.redeemed_by.add(request.user)
    if coupon.type == 'single':
        coupon.is_active = False
    coupon.save()

    return render(request, "herocoupon/success.html", {'code': code, 'xp': coupon.xp})