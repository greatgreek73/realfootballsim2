from django.contrib import admin
from .models import Season, League, Championship, ChampionshipTeam, ChampionshipMatch

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'level', 'max_teams', 'foreign_players_limit')
    list_filter = ('country', 'level')
    search_fields = ('name',)
    ordering = ['country', 'level']

class ChampionshipTeamInline(admin.TabularInline):
    model = ChampionshipTeam
    extra = 0
    fields = ('team', 'points', 'matches_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against')
    readonly_fields = ('points', 'matches_played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against')

class ChampionshipMatchInline(admin.TabularInline):
    model = ChampionshipMatch
    extra = 0
    fields = ('match', 'round', 'match_day', 'processed')
    readonly_fields = ('processed',)

@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = ('league', 'season', 'status', 'start_date', 'end_date', 'match_time')
    list_filter = ('status', 'season', 'league')
    search_fields = ('league__name', 'season__name')
    inlines = [ChampionshipTeamInline, ChampionshipMatchInline]
    
    fieldsets = (
        (None, {
            'fields': ('season', 'league', 'status')
        }),
        ('Даты и время', {
            'fields': ('start_date', 'end_date', 'match_time'),
            'description': 'Время начала матчей указывается в UTC'
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'pending':
            return ['season', 'league', 'start_date']
        return []

@admin.register(ChampionshipTeam)
class ChampionshipTeamAdmin(admin.ModelAdmin):
    list_display = ('team', 'championship', 'points', 'matches_played', 
                   'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goals_difference')
    list_filter = ('championship',)
    search_fields = ('team__name', 'championship__league__name')
    readonly_fields = ('points', 'matches_played', 'wins', 'draws', 
                      'losses', 'goals_for', 'goals_against', 'goals_difference')

@admin.register(ChampionshipMatch)
class ChampionshipMatchAdmin(admin.ModelAdmin):
    list_display = ('match', 'championship', 'round', 'match_day', 'processed')
    list_filter = ('championship', 'round', 'processed')
    search_fields = ('match__home_team__name', 'match__away_team__name')
    readonly_fields = ('processed',)