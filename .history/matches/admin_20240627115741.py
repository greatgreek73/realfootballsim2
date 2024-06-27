from django.contrib import admin
from .models import Match, MatchEvent

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'minute', 'event_type', 'player')
    list_filter = ('event_type', 'match')
    search_fields = ('match__home_team__name', 'match__away_team__name', 'player__name')