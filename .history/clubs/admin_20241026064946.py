from django.contrib import admin
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (..., 'is_bot')  # добавьте 'is_bot' к существующим полям
    list_filter = (..., 'is_bot')   # добавьте возможность фильтрации по этому полю