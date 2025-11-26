from django.contrib import admin
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'owner', 'is_bot']  # явно перечисляем все поля
    list_filter = ['country', 'is_bot']
    search_fields = ['name', 'owner__username']