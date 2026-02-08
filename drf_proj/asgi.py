"""
ASGI config for drf_proj project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""


import os


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_proj.settings')
http = get_asgi_application()

from chat.routing import websocket_urlpatterns


# def AuthRequiredMiddleware(inner):
#     async def middleware(scope, receive, send):
#         user = scope.get("user", AnonymousUser())

#         if not user.is_authenticated:
#             await send({
#                 "type": "websocket.close",  # The self.close()
#                 "code": 4001,
#             })

#             return
#         return await inner(scope, receive, send)
#     return middleware


application = ProtocolTypeRouter({
    'http': http,
    
    'websocket': AllowedHostsOriginValidator((
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            ))

    ))
}
)
