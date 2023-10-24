"""
WSGI config for apps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')

application = get_wsgi_application()


def post_handler():
    from common.event.listener_manage import ListenerManagement
    ListenerManagement().run()
    ListenerManagement.init_embedding_model_signal.send()


post_handler()
