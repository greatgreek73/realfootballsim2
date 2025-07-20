#!/usr/bin/env python3
"""
Тест с принудительным использованием SQLite
"""

import os
import sys
import django

# Принудительно используем SQLite
os.environ['USE_SQLITE'] = '1'

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')

# Переопределяем настройки базы данных до инициализации Django
from django.conf import settings
if not settings.configured:
    settings.configure(
        **{
            'DATABASES': {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '/mnt/c/realfootballsim/db.sqlite3',
                }
            },
            'INSTALLED_APPS': [
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'clubs',
                'players',
                'matches',
                'tournaments',
            ],
            'SECRET_KEY': 'test-key',
            'USE_TZ': True,
        }
    )

django.setup()

from clubs.models import Club
from players.models import Player

def test_sqlite_data():
    """Тестируем данные в SQLite"""
    
    print("ТЕСТ ДАННЫХ В SQLITE")
    print("=" * 40)
    
    try:
        # Проверяем общее количество клубов
        clubs_count = Club.objects.count()
        print(f"Всего клубов в SQLite: {clubs_count}")
        
        # Ищем клуб с ID 321
        try:
            club_321 = Club.objects.get(id=321)
            print(f"Клуб ID 321: {club_321.name}")
            
        except Club.DoesNotExist:
            print("Клуб с ID 321 не найден в SQLite")
            
            # Ищем Hereford United по имени
            hereford_clubs = Club.objects.filter(name__icontains="Hereford")
            print(f"Клубы с 'Hereford' в названии: {hereford_clubs.count()}")
            
            for club in hereford_clubs:
                print(f"  ID {club.id}: {club.name}")
                
        # Проверяем всех вратарей
        goalkeepers = Player.objects.filter(position="Goalkeeper")
        print(f"Всего вратарей в SQLite: {goalkeepers.count()}")
        
        # Проверяем первых 5 вратарей
        print(f"\nПервые 5 вратарей:")
        for gk in goalkeepers[:5]:
            print(f"  {gk.first_name} {gk.last_name} ({gk.club.name if gk.club else 'Без клуба'})")
            print(f"    ПАС: {gk.passing}, ВИДЕНИЕ: {gk.vision}")
            
    except Exception as e:
        print(f"Ошибка при работе с SQLite: {e}")

if __name__ == "__main__":
    test_sqlite_data()