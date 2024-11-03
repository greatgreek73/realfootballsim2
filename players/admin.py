from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'club', 'nationality')
    list_filter = ('club', 'nationality')
    search_fields = ('last_name', 'first_name', 'club__name', 'nationality')

# или можно использовать
# admin.site.register(Player, PlayerAdmin)
