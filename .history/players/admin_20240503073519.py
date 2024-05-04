from django.contrib import admin
from .models import Position, Player, Characteristic

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'club', 'position')  # Убедитесь, что здесь используется 'position'
    list_filter = ('position',)  # Фильтрация теперь по 'position'

class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')  # Обновленный список отображаемых полей
    list_filter = ('type',)  # Фильтр по типу характеристики

admin.site.register(Position)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
