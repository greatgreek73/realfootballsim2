#!/usr/bin/env python3
"""
Тест подключения к базе данных и проверка данных Hereford United
"""

import os
import sys
import django

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from django.db import connection
from clubs.models import Club
from players.models import Player

def test_database_connection():
    """Тестирует подключение к базе данных и показывает информацию"""
    
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # Информация о текущих настройках базы данных
    db_config = settings.DATABASES['default']
    print(f"ENGINE: {db_config['ENGINE']}")
    print(f"NAME: {db_config['NAME']}")
    print(f"USER: {db_config.get('USER', 'N/A')}")
    print(f"HOST: {db_config.get('HOST', 'N/A')}")
    print(f"PORT: {db_config.get('PORT', 'N/A')}")
    
    # Переменная окружения IS_PRODUCTION
    is_production = os.environ.get('IS_PRODUCTION')
    print(f"IS_PRODUCTION: {is_production}")
    
    try:
        # Тестируем подключение
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ Подключение к базе данных успешно: {result}")
            
        # Проверяем количество клубов
        clubs_count = Club.objects.count()
        print(f"Всего клубов в базе: {clubs_count}")
        
        # Ищем Hereford United
        try:
            hereford = Club.objects.get(id=321)
            print(f"✓ Hereford United найден: {hereford.name}")
            
            # Проверяем игроков
            players_count = hereford.player_set.count()
            goalkeepers_count = hereford.player_set.filter(position="Goalkeeper").count()
            
            print(f"Игроков в Hereford United: {players_count}")
            print(f"Вратарей в Hereford United: {goalkeepers_count}")
            
            # Показываем вратарей
            if goalkeepers_count > 0:
                print(f"\nВРАТАРИ HEREFORD UNITED:")
                for gk in hereford.player_set.filter(position="Goalkeeper"):
                    print(f"  {gk.first_name} {gk.last_name}")
                    print(f"    ПАС: {gk.passing}")
                    print(f"    ВИДЕНИЕ: {gk.vision}")
                    print(f"    ВЫНОСЛИВОСТЬ: {gk.stamina}")
                    print(f"    МОРАЛЬ: {gk.morale}")
                    print(f"    РАСПРЕДЕЛЕНИЕ: {gk.distribution}")
                    print()
            else:
                print("❌ Вратари не найдены в Hereford United!")
                
        except Club.DoesNotExist:
            print("❌ Hereford United (ID 321) не найден в базе данных!")
            
            # Показываем первые 10 клубов для справки
            print(f"\nПервые 10 клубов в базе:")
            for club in Club.objects.all()[:10]:
                print(f"  ID {club.id}: {club.name}")
                
        except Exception as e:
            print(f"❌ Ошибка при поиске Hereford United: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        print("Возможно, PostgreSQL не запущен или настройки подключения неверны")
        
        # Проверяем наличие SQLite файла как fallback
        sqlite_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        if os.path.exists(sqlite_path):
            print(f"📁 Найден SQLite файл: {sqlite_path}")
            print("Возможно, нужно временно переключиться на SQLite для тестирования")
        else:
            print("📁 SQLite файл не найден")

if __name__ == "__main__":
    test_database_connection()