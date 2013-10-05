"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_webtest import WebTest
from django_dynamic_fixture import G
from heroorganization.models import Organization


class OrganizationTest(WebTest):
    def test_show_org_profile_instead_of_hero_profile_if_user_is_organization(self):
        organization = G(Organization, user__username='anorg')
        url = reverse("userprofile_public", args=(organization.user.username, ))
        profile = self.app.get(url, user=organization.user)
        self.assertRedirects(profile, reverse("organization_detail",
                                              args=(organization.user.username, )))
        self.assertContains(profile.follow(), organization.user.profile.about)

    def test_organization_update_not_allowed_for_other_user(self):
        user = G(User)
        self.app.get(reverse("organization_update"), user=user, status=403)

    def test_organization_update(self):
        organization = G(Organization)
        update_page = self.app.get(reverse("organization_update"), user=organization.user)
        self.assertContains(update_page, organization.name)
        form = update_page.forms[0]

        form['about'] = 'anewdescription'
        response = form.submit()

        self.assertRedirects(response, reverse("organization_update"))
        self.assertEqual(User.objects.get(pk=organization.user_id).profile.about, "anewdescription")