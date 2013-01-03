from django.dispatch import Signal

apply = Signal(providing_args=['quest'])
like = Signal(providing_args=['quest'])
participate = Signal(providing_args=['quest'])
participate_plus= Signal(providing_args=['quest'])
