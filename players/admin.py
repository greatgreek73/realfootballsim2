from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('club', 'age', 'nationality')
    list_filter = ('club', 'nationality')
    search_fields = ('club__name', 'nationality')

# или можно использовать
# admin.site.register(Player, PlayerAdmin)
