import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models
from matches.models import Match, MatchEvent

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f"match_{self.match_id}"

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Обычно клиент не посылает ничего, либо мы можем обработать при необходимости
        pass

    # Метод для отправки сообщений в WebSocket
    async def match_update(self, event):
        # event содержит 'type': 'match_update' и 'data': словарь с информацией
        await self.send(json.dumps(event['data']))
