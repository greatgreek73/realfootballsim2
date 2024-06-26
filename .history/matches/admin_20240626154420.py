from django.contrib import admin
from .models import Match, TeamSelection

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(TeamSelection)
class TeamSelectionAdmin(admin.ModelAdmin):
    list_display = ('match', 'club', 'created_at', 'updated_at')
    list_filter = ('club', 'created_at', 'updated_at')
    search_fields = ('match__home_team__name', 'match__away_team__name', 'club__name')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('match', 'club', 'selection')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False