#noinspection PyUnresolvedReferences
from os import path
import socket

settings_dir = path.dirname(__file__)
if path.exists(path.join(settings_dir, 'local.py')):
    from .local import *
elif socket.gethostname() == "youarehero.vagrant":
    from .vagrant import *
else:
    from .devel import *
