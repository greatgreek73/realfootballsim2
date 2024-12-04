from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from .models import Match, MatchEvent

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'datetime', 'status', 'processed')
    list_filter = ('status', ('datetime', DateFieldListFilter), 'processed')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'minute', 'event_type', 'player')
    list_filter = ('event_type', 'match')
    search_fields = ('match__home_team__name', 'match__away_team__name', 'player__first_name', 'player__last_name')