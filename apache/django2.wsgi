import os
import sys

path = '/usr/local/mbaproject'
project = '/webMBArepo'
if path not in sys.path:
    sys.path.append(path)
    sys.path.append(path+project)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webMBArepo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

