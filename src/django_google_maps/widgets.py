from django.forms.widgets import HiddenInput
import types
from django.conf import settings
from django.forms import widgets
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django_google_maps.fields import GeoPt
from easy_maps.widgets import AddressWithMapWidget
from django.template import Template, Context
from django.forms import TextInput


class GoogleMapsAddressWidget(TextInput):
    "a widget that will place a google map right after the #id_address field"

    def __init__(self, *args, **kwargs):
        super(GoogleMapsAddressWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        lat, lng = None, None

        if not isinstance(value, GeoPt):
            value = GeoPt(value)

        lat = value.lat
        lng = value.lon


        default_html = HiddenInput().render(name, value, attrs)
        context = Context({'lat': lat, 'lng': lng,})
        templateString = "{%% load easy_maps_tags %%}{%% easy_map %s %s 400 300 16 using 'easy_maps/map.html'%%}" % (lat,lng)
        map_template = Template(templateString)
        return default_html + map_template.render(context)

  #  def render(self, name, value, attrs=None):
  #      if value is None:
  #          value = ''
   #     final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
   #     if value != '':
    #        # Only add the 'value' attribute if a value is non-empty.
     #       final_attrs['value'] = force_unicode(self._format_value(value))
      #  return mark_safe(
       # '<script type="application/javascript" src="https://maps.google.com/maps/api/js?sensor=false"></script>'
       # '<script type="application/javascript" src="%sdjango_google_maps/js/google-maps-admin.js"></script>'
       #     u'<input%s /><div class="map_canvas_wrapper"><div id="map_canvas"></div></div>' % (settings.STATIC_URL, flatatt(final_attrs))#
#
 #       )