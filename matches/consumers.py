# matches/consumers.py
import logging
import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from .models import Match, MatchEvent

logger = logging.getLogger('match_creation')

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f"match_{self.match_id}"

        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            logger.info(f'[WebSocket] Подключение установлено: матч ID={self.match_id}, канал {self.channel_name}')
            print(f"WebSocket accepted for match {self.match_id}")

            match_data = await self.get_match_data()
            if match_data:
                await self.send(text_data=json.dumps({
                    'type': 'match_update',
                    'data': match_data
                }, cls=DjangoJSONEncoder))
                print("Initial match data sent")
            else:
                logger.warning(f'[WebSocket] Матч ID={self.match_id} не найден — отправка ошибки клиенту и закрытие соединения')
                print(f"No match data found for ID: {self.match_id}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Match not found'
                }))
                await self.close()

        except Exception as e:
            logger.error(f'[WebSocket] Ошибка в connect для матча ID={self.match_id}: {e}')
            print(f"Error in connect for match {self.match_id}: {e}")
            traceback.print_exc()
            await self.close(code=1011)

    async def disconnect(self, close_code):
        logger.info(f'[WebSocket] Отключение: матч ID={self.match_id}, код={close_code}, канал={self.channel_name}')
        print(f"WebSocket disconnecting from match {self.match_id} (code {close_code})")
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f'[WebSocket] Клиент удалён из группы {self.group_name}')
            print(f"Removed from group {self.group_name}")
        except Exception as e:
            logger.error(f'[WebSocket] Ошибка в disconnect для матча ID={self.match_id}: {e}')
            print(f"Error in disconnect for match {self.match_id}: {e}")

    async def receive_json(self, content, **kwargs):
        """Handle control messages from the client."""
        try:
            if content.get("type") == "control" and content.get("action") == "next_minute":
                status = await self.get_match_status()
                if status == "paused":
                    await self.update_match_status("in_progress")
        except Exception as e:
            logger.error(f"Error processing incoming message for match {self.match_id}: {e}")


    async def match_update(self, event):
        try:
            data = event.get('data', {})
            
            # ИСПРАВЛЕНИЕ: Проверяем, является ли это частичным обновлением с событием
            if data.get('partial_update') and 'events' in data:
                # Для частичных обновлений с событиями просто отправляем данные как есть
                # НЕ загружаем все события из БД заново
                await self.send(text_data=json.dumps({
                    'type': 'match_update',
                    'data': data
                }, cls=DjangoJSONEncoder))
                print(f"Sent partial update with event to client for match {self.match_id}")
            else:
                # Для обычных обновлений состояния (без событий) или полных обновлений
                is_partial = 'minute' not in data or 'status' not in data

                if is_partial:
                    print(f"Partial update for match {self.match_id}, fetching full data...")
                    full = await self.get_match_data()
                    if not full:
                        print(f"Unable to fetch full match data for {self.match_id}")
                        return
                    # Обновляем только те поля, которые пришли в data
                    full.update(data)
                    # НЕ перезаписываем события, если они не пришли в обновлении
                    if 'events' in data:
                        full['events'] = data['events']
                    payload = full
                else:
                    print(f"Full update for match {self.match_id}")
                    payload = data

                await self.send(text_data=json.dumps({
                    'type': 'match_update',
                    'data': payload
                }, cls=DjangoJSONEncoder))
                print(f"Sent update to client for match {self.match_id}")

        except Exception as e:
            print(f"Error in match_update for match {self.match_id}: {e}")
            traceback.print_exc()

    @database_sync_to_async
    def get_match_data(self):
        try:
            match = Match.objects.select_related(
                'home_team',
                'away_team',
                'current_player_with_ball',
            ).get(id=self.match_id)

            # Не загружаем события текущей минуты для live-матча
            # Они придут через broadcast
            if match.status == 'in_progress':
                all_events = (
                    MatchEvent.objects
                    .filter(match_id=self.match_id)
                    .exclude(minute=match.current_minute)  # Исключаем текущую минуту
                    .select_related('player', 'related_player')
                    .order_by('minute', 'timestamp')
                )
                logger.info(f'[WebSocket] Загружаем события для матча {self.match_id}, исключая текущую минуту {match.current_minute}')
            else:
                # Для завершенных матчей загружаем все
                all_events = (
                    MatchEvent.objects
                    .filter(match_id=self.match_id)
                    .select_related('player', 'related_player')
                    .order_by('minute', 'timestamp')
                )

            events_list = []
            for evt in all_events:
                events_list.append({
                    'minute': evt.minute,
                    'event_type': evt.event_type,
                    'description': evt.description,
                    'player_name': evt.player.last_name if evt.player else None,
                    'related_player_name': evt.related_player.last_name if evt.related_player else None,
                })

            possessing_team_id = None
            if match.possession_indicator == 1:
                possessing_team_id = str(match.home_team_id)
            elif match.possession_indicator == 2:
                possessing_team_id = str(match.away_team_id)

            return {
                "match_id": str(match.id),
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "st_shoots": match.st_shoots,
                "st_passes": match.st_passes,
                "st_possessions": match.st_possessions,
                "st_fouls": match.st_fouls,
                "st_injury": [] if match.st_injury == 0 else [{"message": f"Травм: {match.st_injury}"}],
                "events": events_list,
                "status": match.status,
                "current_player": (
                    str(match.current_player_with_ball.id)
                    if match.current_player_with_ball else None
                ),
                "current_zone": match.current_zone,
                "possessing_team_id": possessing_team_id,
            }

        except Match.DoesNotExist:
            print(f"Match {self.match_id} not found")
            return None
        except Exception as e:
            print(f"Error getting match data for match {self.match_id}: {e}")
            traceback.print_exc()
            return None

    @database_sync_to_async
    def get_match_status(self):
        try:
            return Match.objects.get(id=self.match_id).status
        except Match.DoesNotExist:
            return None

    @database_sync_to_async
    def update_match_status(self, status: str):
        Match.objects.filter(id=self.match_id).update(status=status)
