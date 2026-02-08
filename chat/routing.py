
from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$",
            consumers.LocalChatConsumer.as_asgi()),

    re_path(r"ws/support_chat/(?P<user>[\w.@+-]+)/(?P<admin>[\w.@+-]+)/$",
            consumers.AdminChatConsumer.as_asgi())


]
