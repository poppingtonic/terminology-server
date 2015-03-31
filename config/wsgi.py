# coding=utf-8
"""
WSGI config for terminology server project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # NOQA
application = get_wsgi_application()
