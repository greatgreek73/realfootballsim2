import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Match

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connect attempt...")
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f"match_{self.match_id}"

        # Debug prints
        print(f"Match ID: {self.match_id}")
        print(f"Group name: {self.group_name}")
        
        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print("Successfully added to channel group")
            
            await self.accept()
            print("WebSocket connection accepted")

            # Получаем последние данные матча и сразу отправляем их
            match = await self.get_match_data()
            if match:
                await self.send(text_data=json.dumps({
                    "minute": match["current_minute"],
                    "home_score": match["home_score"],
                    "away_score": match["away_score"],
                    "events": match["events"]
                }))
                print("Initial match data sent")
            
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            raise

    async def disconnect(self, close_code):
        print(f"WebSocket disconnecting... Code: {close_code}")
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print("Successfully removed from channel group")
        except Exception as e:
            print(f"Error in disconnect: {str(e)}")

    async def match_update(self, event):
        """
        Стандартное событие для отправки «полного» обновления матча:
          data = {
             "minute": ...,
             "home_score": ...,
             "away_score": ...,
             "events": [...],
             ...
          }
        """
        print(f"Received match update: {event}")
        try:
            await self.send(text_data=json.dumps(event['data']))
            print("Successfully sent match update to client")
        except Exception as e:
            print(f"Error sending match update: {str(e)}")

    async def match_partial_update(self, event):
        """
        Событие для «порционного» (частичного) обновления.
        Предполагается, что event['data'] может содержать часть событий
        (например, за один из "подотрезков" внутри минуты).
        """
        print(f"Received partial match update: {event}")
        try:
            await self.send(text_data=json.dumps(event['data']))
            print("Successfully sent partial update to client")
        except Exception as e:
            print(f"Error sending partial update: {str(e)}")

    @database_sync_to_async
    def get_match_data(self):
        """
        Извлекает из БД основные данные матча + все события,
        чтобы при подключении WebSocket клиент сразу их увидел.
        """
        from .models import MatchEvent  # локальный импорт, если нужно
        try:
            match = Match.objects.get(id=self.match_id)
            return {
                "current_minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "events": list(
                    match.events.all().values('minute', 'event_type', 'description')
                ),
            }
        except Match.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting match data: {str(e)}")
            return None
