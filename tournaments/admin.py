from django.contrib import admin
from django.core.management import call_command
from django.contrib import messages

from .models import (
    Season,
    League,
    Championship,
    ChampionshipTeam,
    ChampionshipMatch
)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('-start_date',)
    actions = ['end_season', 'force_end_season']

    def end_season(self, request, queryset):
        """Завершает выбранный сезон через management-команду."""
        if queryset.count() > 1:
            messages.error(request, "Can only end one season at a time.")
            return

        season = queryset.first()
        if not season.is_active:
            messages.error(request, "Can only end active season.")
            return

        try:
            call_command('end_season')
            messages.success(request, f"Successfully ended season {season.number}")
        except Exception as e:
            messages.error(request, f"Error ending season: {str(e)}")

    end_season.short_description = "End selected season"

    def force_end_season(self, request, queryset):
        """Принудительно завершает сезон (пропускает валидации)."""
        if queryset.count() > 1:
            messages.error(request, "Can only end one season at a time.")
            return

        season = queryset.first()
        if not season.is_active:
            messages.error(request, "Can only end active season.")
            return

        try:
            call_command('end_season', '--force')
            messages.success(request, f"Successfully force ended season {season.number}")
        except Exception as e:
            messages.error(request, f"Error force ending season: {str(e)}")

    force_end_season.short_description = "Force end selected season (skip validations)"


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'level', 'max_teams')
    list_filter = ('country', 'level')
    search_fields = ('name',)
    ordering = ['country', 'level']


class ChampionshipTeamInline(admin.TabularInline):
    model = ChampionshipTeam
    extra = 0
    fields = (
        'team', 'points', 'matches_played',
        'wins', 'draws', 'losses',
        'goals_for', 'goals_against', 'goals_difference'
    )
    readonly_fields = (
        'points', 'matches_played',
        'wins', 'draws', 'losses',
        'goals_for', 'goals_against', 'goals_difference'
    )
    ordering = ('-points', '-goals_for')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ChampionshipMatchInline(admin.TabularInline):
    model = ChampionshipMatch
    extra = 0
    show_change_link = True


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = (
        'league', 'season', 'status', 'start_date',
        'end_date', 'total_matches', 'finished_matches', 'match_time'
    )
    list_filter = ('status', 'season', 'league')
    search_fields = ('league__name', 'season__name')
    inlines = [ChampionshipTeamInline, ChampionshipMatchInline]

    def get_readonly_fields(self, request, obj=None):
        # Когда статус != 'pending', запрещаем редактировать часть полей.
        if obj and obj.status != 'pending':
            return ['season', 'league', 'start_date']
        return []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def total_matches(self, obj):
        return obj.championshipmatch_set.count()

    total_matches.short_description = "Total Matches"

    def finished_matches(self, obj):
        return obj.championshipmatch_set.filter(match__status='finished').count()

    finished_matches.short_description = "Finished Matches"


@admin.register(ChampionshipTeam)
class ChampionshipTeamAdmin(admin.ModelAdmin):
    list_display = (
        'team', 'championship', 'points',
        'matches_played', 'wins', 'draws',
        'losses', 'goals_for', 'goals_against',
        'goals_difference'
    )
    list_filter = ('championship',)
    search_fields = ('team__name', 'championship__league__name')
    readonly_fields = (
        'points', 'matches_played', 'wins',
        'draws', 'losses', 'goals_for',
        'goals_against', 'goals_difference'
    )
    ordering = ('-points', '-goals_for')


@admin.register(ChampionshipMatch)
class ChampionshipMatchAdmin(admin.ModelAdmin):
    list_display = (
        'match', 'championship', 'round',
        'match_day', 'status', 'score'
    )
    list_filter = ('championship', 'round', 'match__status')
    search_fields = ('match__home_team__name', 'match__away_team__name')
    readonly_fields = ('processed',)

    def status(self, obj):
        return obj.match.get_status_display()

    status.short_description = "Status"

    def score(self, obj):
        if obj.match.status == 'finished':
            return f"{obj.match.home_score} - {obj.match.away_score}"
        return "-"

    score.short_description = "Score"
