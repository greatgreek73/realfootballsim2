from django.contrib import admin
from .models import Position, Player, Characteristic, PlayerCharacteristic

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'club', 'position')  # Убедитесь, что здесь используется 'position'
    list_filter = ('position',)  # Фильтрация теперь по 'position'

class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')  # Обновленный список отображаемых полей
    list_filter = ('type',)  # Фильтр по типу характеристики

class PlayerCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('player', 'characteristic', 'value')  # Отображение игрока, характеристики и значения
    list_filter = ('player', 'characteristic')  # Фильтрация по игроку и характеристике
    search_fields = ('player__name', 'characteristic__name')  # Поиск по имени игрока и названию характеристики

admin.site.register(Position)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
admin.site.register(PlayerCharacteristic, PlayerCharacteristicAdmin)  # Регистрация нового класса администратора
