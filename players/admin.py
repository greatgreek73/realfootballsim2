from django.contrib import admin
from .models import Player, TrainingSettings

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'club', 'nationality', 'age', 'bloom_type', 'is_in_bloom')
    list_filter = ('club', 'nationality', 'bloom_type', 'position')
    search_fields = ('last_name', 'first_name', 'club__name', 'nationality')
    readonly_fields = ('is_in_bloom',)

@admin.register(TrainingSettings)
class TrainingSettingsAdmin(admin.ModelAdmin):
    list_display = ('player', 'get_player_position', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('player__last_name', 'player__first_name', 'player__club__name')
    
    def get_player_position(self, obj):
        return obj.player.position
    get_player_position.short_description = 'Position'
