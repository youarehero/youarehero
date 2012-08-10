#coding: utf-8
from django import template
from django.template.loader import render_to_string
from easy_maps.models import Address
from herobase.models import UserProfile

register = template.Library()

@register.tag
def easy_map(parser, token):
    """
    The syntax:
        {% easy_map <address> [<width> <height>] [<zoom>] [using <template_name>] %}
    """
    lat, lng, width, height, zoom, markertext, template_name = None, None, None, None, None, None, None
    params = token.split_contents()

    # pop the template name
    if params[-2] == 'using':
        template_name = params[-1]
        params = params[:-2]

    if len(params) < 3:
        raise template.TemplateSyntaxError('easy_map tag requires geo coordinates argument')

    lat = params[1]
    lng = params[2]

    if len(params) == 5:
        width, height = params[3], params[4]
    elif len(params) == 6:
        width, height, zoom = params[3], params[4], params[5]
    elif len(params) == 7:
        width, height, zoom, markertext = params[3], params[4], params[5], params[6]
    elif len(params) == 4 or len(params) > 7:
        raise template.TemplateSyntaxError('easy_map tag has the following syntax: '
                   '{% easy_map <lat> <lng> <width> <height> [zoom] [using <template_name>] %}')
    return EasyMapNode(lat, lng, width, height, zoom, markertext, template_name)

class EasyMapNode(template.Node):
    def __init__(self, lat, lng, width, height, zoom, markertext, template_name):

        self.lat = template.Variable(lat)
        self.lng = template.Variable(lng)
        self.width = width or ''
        self.height = height or ''
        self.zoom = zoom or 16
        self.template_name = template.Variable(template_name or '"easy_maps/map.html"')

    def render(self, context):
        try:
            lat = self.lat.resolve(context)
            lng = self.lng.resolve(context)
            template_name = self.template_name.resolve(context)
            context.update({
                'lat' : lat,
                'lng' : lng,
                'width': self.width,
                'height': self.height,
                'zoom': self.zoom,
                'template_name': template_name
            })
            return render_to_string(template_name, context_instance=context)
        except template.VariableDoesNotExist:
            return ''
