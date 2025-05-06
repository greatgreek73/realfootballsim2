import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# Убедитесь, что импортируете модели правильно
from .models import Match, MatchEvent, Player
from django.core.serializers.json import DjangoJSONEncoder
import traceback # Для более детального логгирования ошибок

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
            print(f"WebSocket accepted for match {self.match_id}")

            match_data = await self.get_match_data()
            if match_data:
                message_to_send = {
                    'type': 'match_update',
                    'data': match_data
                }
                await self.send(text_data=json.dumps(message_to_send, cls=DjangoJSONEncoder))
                print("Initial match data sent (wrapped)")
            else:
                print(f"No match data found for ID: {self.match_id}")
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Match not found'}))
                await self.close()

        except Exception as e:
            print(f"Error in connect for match {self.match_id}: {str(e)}")
            traceback.print_exc()
            await self.close(code=1011)

    async def disconnect(self, close_code):
        print(f"WebSocket disconnecting from match {self.match_id}... Code: {close_code}")
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"Successfully removed from channel group {self.group_name}")
        except Exception as e:
            print(f"Error in disconnect for match {self.match_id}: {str(e)}")

    async def match_update(self, event):
        """Отправляет обновление состояния матча клиенту"""
        try:
            print(f"Received event for group {self.group_name}: {event.keys()}")
            update_data = event.get('data', event)
            if not isinstance(update_data, dict):
                 print(f"Error: Expected dict in event['data'] or event, got {type(update_data)}. Event: {event}")
                 return

            is_partial = 'minute' not in update_data or 'status' not in update_data

            final_data_to_send = {}
            if is_partial:
                print(f"Partial update received for match {self.match_id}. Keys: {update_data.keys()}. Fetching full data...")
                full_match_data = await self.get_match_data()
                if full_match_data:
                    full_match_data.update(update_data)
                    if 'events' in update_data: # Убедимся, что события из частичного обновления перетирают старые
                       full_match_data['events'] = update_data['events']
                    final_data_to_send = full_match_data
                else:
                    print(f"Error: Could not get full match data for {self.match_id} during partial update processing.")
                    return
            else:
                 print(f"Full update received for match {self.match_id}.")
                 final_data_to_send = update_data

            message_to_send = {
                'type': 'match_update',
                'data': final_data_to_send
            }
            await self.send(text_data=json.dumps(message_to_send, cls=DjangoJSONEncoder))
            print(f"Successfully sent match update to client for match {self.match_id}")

        except Exception as e:
            print(f"Error in match_update for match {self.match_id}: {str(e)}")
            traceback.print_exc()

    @database_sync_to_async
    def get_match_data(self):
        """Получает актуальные данные матча из БД."""
        try:
            match = Match.objects.select_related(
                'home_team',
                'away_team',
                'current_player_with_ball',
            ).prefetch_related(
                models.Prefetch(
                    'events',
                    queryset=MatchEvent.objects.select_related('player', 'related_player')
                                            .order_by('-timestamp')[:10] # 10 последних событий
                )
            ).get(id=self.match_id)

            current_player_id = str(match.current_player_with_ball.id) if match.current_player_with_ball else None

            # --- ИСПОЛЬЗУЕМ НОВОЕ ИМЯ ПОЛЯ ---
            possessing_team_id_val = None
            if match.possession_indicator == 1: # ИЗМЕНЕНО: curent_posses -> possession_indicator
                possessing_team_id_val = str(match.home_team_id)
            elif match.possession_indicator == 2: # ИЗМЕНЕНО: curent_posses -> possession_indicator
                possessing_team_id_val = str(match.away_team_id)
            # --------------------------------

            events_list = []
            for event in match.events.all(): # Используем предзагруженные события
                event_data = {
                    'minute': event.minute,
                    'event_type': event.event_type,
                    'description': event.description,
                    'player_name': event.player.last_name if event.player else None,
                    'related_player_name': event.related_player.last_name if event.related_player else None
                }
                events_list.append(event_data)

            injury_info = match.st_injury

            return {
                "match_id": str(match.id),
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "st_shoots": match.st_shoots,
                "st_passes": match.st_passes,
                # Используем ИСПРАВЛЕННОЕ имя поля
                "st_possessions": match.st_possessions,
                "st_fouls": match.st_fouls,
                # Временная заглушка для травм (нужно решить, как хранить/передавать)
                "st_injury": [] if injury_info == 0 else [{'message': f'Травм: {injury_info}'}],
                "events": events_list,
                "status": match.status,
                "current_player": current_player_id,
                "current_zone": match.current_zone,
                "possessing_team_id": possessing_team_id_val
            }
        except Match.DoesNotExist:
            print(f"Match {self.match_id} not found in get_match_data")
            return None
        except Exception as e:
            print(f"Error getting match data for match {self.match_id}: {str(e)}")
            traceback.print_exc()
            return None