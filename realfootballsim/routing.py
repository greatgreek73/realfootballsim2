from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from matches.consumers import MatchConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/match/<int:match_id>/", MatchConsumer.as_asgi()),
    ]),
})
