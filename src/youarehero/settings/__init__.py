#noinspection PyUnresolvedReferences
from os import path

settings_dir = path.dirname(__file__)
if path.exists(path.join(settings_dir, 'local.py')):
    from .local import *
else:
    from .devel import *
