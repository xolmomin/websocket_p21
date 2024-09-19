from django.urls import re_path

from apps import consumers

websocket_urlpatterns = [
    re_path('ws/chat', consumers.ChatConsumer.as_asgi()),
]
