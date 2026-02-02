"""
ASGI config for verdadoreto project.

Expone la aplicación ASGI con soporte para HTTP y WebSockets (Django Channels).

Más información:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verdadoreto.settings')
django_asgi_app = get_asgi_application()

# En desarrollo, servir también los estáticos vía ASGI
from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
    django_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from channels.auth import AuthMiddlewareStack
from django.urls import path
from verdadoreto_app.consumers import RoomConsumer

# Router principal: HTTP va a Django; WebSocket va a Channels (AuthMiddlewareStack + URLRouter)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/rooms/<str:code>/", RoomConsumer.as_asgi()),
            ])
        )
    ),
})
