"""
WSGI config for tienda_celulares project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_celulares.settings')

application = get_wsgi_application()
