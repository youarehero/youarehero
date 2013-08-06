"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_webtest import WebTest
from heroorganization.models import Organization


class OrganizationTest(WebTest):
    def test_show_org_profile_instead_of_hero_profile_if_user_is_organization(self):
        user = User.objects.create(username='tester', email='test@example.com')
        organization = Organization.objects.create(
            user=User.objects.create(username='eineorg'),
            description="orgdescription")
        url = reverse("userprofile_public", args=(organization.user.username, ))
        profile = self.app.get(url, user=user)
        self.assertRedirects(profile, reverse("organization_detail", args=(organization.user.username, )))
        self.assertContains(profile.follow(), organization.description)

    def test_admin_view(self):
        org_user = User.objects.create(username='eineorg')
        organization = Organization.objects.create(user=org_user, description="orgdescription")
        url = reverse("organization_admin_index")
        admin_index = self.app.get(url, user=org_user)
        self.assertContains(admin_index, organization.name)

    def test_admin_update(self):
        org_user = User.objects.create(username='eineorg')
        organization = Organization.objects.create(user=org_user, description="orgdescription")
        url = reverse("organization_admin_update", args=(organization.pk, ))
        edit_page = self.app.get(url, user=org_user)
        self.assertContains(edit_page, organization.name)
        form = edit_page.forms[0]
        form['description'] = 'newdescription'
        updated = form.submit()
        self.assertRedirects(updated, reverse("organization_admin_index"))

    def test_admin_views_need_organization_user(self):
        user = User.objects.create(username='eineorg', email='other')
        organization = Organization.objects.create(user=User.objects.create(email='somemail'))
        self.app.get(reverse("organization_admin_index"), user=user, status=403)
        self.app.get(reverse("organization_admin_update", args=(organization.pk, )),
                     user=user, status=403)
