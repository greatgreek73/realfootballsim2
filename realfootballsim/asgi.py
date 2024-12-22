"""
ASGI config for realfootballsim project.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()  # Важно: setup должен быть до импорта MatchConsumer

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from matches.consumers import MatchConsumer
from django.urls import path

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/match/<int:match_id>/", MatchConsumer.as_asgi()),
        ])
    ),
})