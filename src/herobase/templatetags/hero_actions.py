from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def valid_actions_for(context, instance):
    if not instance:
        return []
    request = context['request']
    return instance.valid_actions_for(request)