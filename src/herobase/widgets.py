"""
Custom Form Widgets for django models.
"""

from django import forms
from django.utils.safestring import mark_safe

DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 300

DEFAULT_LAT = 55.16 #hmm, i like egypt
DEFAULT_LNG = 61.4


class LocationWidget(forms.TextInput):
    """Custom geolocation widget."""
    def __init__(self, *args, **kw):

        """
        credits go to https://gist.github.com/1196589
        + was important to add css styles for correct display

        """
        self.map_width = kw.get("map_width", DEFAULT_WIDTH)
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT)

        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        if value is None:
            lat, lng = DEFAULT_LAT, DEFAULT_LNG
        else:
            if isinstance(value, unicode):
                a, b = value.split(',')
            else:
                a, b = value
            lat, lng = float(a), float(b)

        js = '''
<script type="application/javascript" src="https://maps.google.com/maps/api/js?sensor=false"></script>
<script>

<!--
    var map_%(name)s;
    
    function savePosition_%(name)s(point)
    {
        var input = document.getElementById("id_%(name)s");
        input.value = point.lat().toFixed(6) + "," + point.lng().toFixed(6);
        map_%(name)s.panTo(point);
    }
    
    function load_%(name)s() {
        var point = new google.maps.LatLng(%(lat)f, %(lng)f);

        var options = {
            zoom: 13,
            maxZoom: 13,
            center: point,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControl: false,
            streetViewControl: false,

        };
        
        map_%(name)s = new google.maps.Map(document.getElementById("map_%(name)s"), options);

        var marker = new google.maps.Marker({
                map: map_%(name)s,
                draggable: true,
                position: new google.maps.LatLng(%(lat)f, %(lng)f),
        });
        google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
            savePosition_%(name)s(mouseEvent.latLng);
        });

    }
    
    $(function() {
        load_%(name)s();
    });

//-->
</script>
        ''' % dict(name=name, lat=lat, lng=lng)
        html = self.inner_widget.render("%s" % name, "%f,%f" % (lat, lng), dict(id='id_%s' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (name, self.map_width, self.map_height)

        return mark_safe(js + html)

    #TODO check how to integrate this media with crispy form and change the way script is inserted at top now
    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            )