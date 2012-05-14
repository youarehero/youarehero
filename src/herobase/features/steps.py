from django.contrib.auth.models import User
from lettuce import *
from lxml import html
from django.test.client import Client



@before.all
def set_browser():
    world.browser = Client()

@step(r'I access the url "(.*)"')
def access_url(step, url):
    response = world.browser.get(url)
    world.response = response
    world.dom = html.fromstring(response.content)

@step(r'I see the button "(.*)"')
def see_button(step, text):
    buttons = world.dom.cssselect("button")
    assert buttons
    assert text in [b.text for b in buttons]


@step(r'I am the user "(.*)"')
def am_user(step, username):
    world.user = User.objects.create(username=username)


@step(r'I see the text "(.*)"')
def see_text(step, text):
    print world.response.content
    assert text in world.response.content