from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from matches.consumers import MatchConsumer

websocket_urlpatterns = [
    path("ws/match/<int:match_id>/", MatchConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})