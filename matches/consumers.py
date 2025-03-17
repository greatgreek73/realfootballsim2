import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Match

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connect attempt...")
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f"match_{self.match_id}"

        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Получаем и отправляем начальные данные
            match = await self.get_match_data()
            if match:
                await self.send(text_data=json.dumps(match))
                print("Initial match data sent")
            else:
                print(f"No match data found for ID: {self.match_id}")
                
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
        """Стандартное событие для отправки полного обновления матча"""
        try:
            data = event['data']
            # Проверяем наличие всех необходимых полей
            required_fields = ['minute', 'home_score', 'away_score', 'events', 'status']
            if not all(field in data for field in required_fields):
                print(f"Warning: missing required fields in update. Got: {data.keys()}")
                # Получаем недостающие данные из БД
                match_data = await self.get_match_data()
                if match_data:
                    # Обновляем только новые данные
                    match_data.update(data)
                    data = match_data

            await self.send(text_data=json.dumps(data))
            print("Successfully sent match update to client")
            
        except Exception as e:
            print(f"Error in match_update: {str(e)}")

    async def match_partial_update(self, event):
        """Частичное обновление тоже должно содержать все поля"""
        await self.match_update(event)

    @database_sync_to_async
    def get_match_data(self):
        try:
            match = Match.objects.get(id=self.match_id)
            return {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "st_shoots": match.st_shoots,
                "st_passes": match.st_passes,
                "st_posessions": match.st_posessions,
                "st_fouls": match.st_fouls,
                "events": list(
                    match.events.all().values(
                        'minute', 
                        'event_type', 
                        'description'
                    ).order_by('-minute')[:10]  # Последние 10 событий
                ),
                "status": match.status
            }
        except Match.DoesNotExist:
            print(f"Match {self.match_id} not found")
            return None
        except Exception as e:
            print(f"Error getting match data: {str(e)}")
            return None