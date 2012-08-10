from django.forms import TextInput
from django.template import Template, Context

class AddressWithMapWidget(TextInput):
    def render(self, name, value, attrs=None):
        default_html = super(AddressWithMapWidget, self).render(name, value, attrs)
        map_template = Template("{% load easy_maps_tags %}{% easy_map address 400 300 16 using 'easy_maps/map.html'%}")
        context = Context({'address': value})
        return default_html + map_template.render(context)

