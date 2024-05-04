from django.contrib import admin
from .models import Position, Player, Characteristic, PlayerCharacteristic

class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_value')
    search_fields = ('name',)

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'club', 'position')
    list_filter = ('position', 'club')

admin.site.register(Position)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
