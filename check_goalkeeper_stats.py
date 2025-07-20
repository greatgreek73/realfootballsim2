#!/usr/bin/env python3
"""
Проверяет реальные характеристики вратарей в базе данных
"""

import os
import sys
import django

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from players.models import Player

def check_goalkeepers():
    """Проверяет характеристики всех вратарей в базе"""
    
    print("ПРОВЕРКА ХАРАКТЕРИСТИК ВРАТАРЕЙ")
    print("=" * 50)
    
    # Получаем всех вратарей
    goalkeepers = Player.objects.filter(position="Goalkeeper")
    
    if not goalkeepers:
        print("Вратари не найдены в базе данных!")
        return
    
    print(f"Найдено вратарей: {goalkeepers.count()}")
    print()
    
    for i, gk in enumerate(goalkeepers[:10]):  # Показываем первых 10
        print(f"{i+1}. {gk.first_name} {gk.last_name} ({gk.club.name if gk.club else 'Без клуба'})")
        print(f"   ПАС: {gk.passing}")
        print(f"   ВИДЕНИЕ: {gk.vision}")
        print(f"   ВЫНОСЛИВОСТЬ: {gk.stamina}")
        print(f"   МОРАЛЬ: {gk.morale}")
        print(f"   ПОЗИЦИОНИРОВАНИЕ: {gk.positioning}")
        print(f"   --- Вратарские характеристики ---")
        print(f"   РЕФЛЕКСЫ: {gk.reflexes}")
        print(f"   ЛОВЛЯ: {gk.handling}")
        print(f"   РАСПРЕДЕЛЕНИЕ: {gk.distribution}")
        print(f"   ОБЩИЙ РЕЙТИНГ: {gk.overall_rating}")
        print()
    
    # Статистика по пасу и видению
    zero_passing = goalkeepers.filter(passing=0).count()
    zero_vision = goalkeepers.filter(vision=0).count()
    
    print("СТАТИСТИКА:")
    print(f"Вратарей с нулевым пасом: {zero_passing}/{goalkeepers.count()}")
    print(f"Вратарей с нулевым видением: {zero_vision}/{goalkeepers.count()}")
    
    # Средние значения
    avg_passing = sum(gk.passing for gk in goalkeepers) / goalkeepers.count()
    avg_vision = sum(gk.vision for gk in goalkeepers) / goalkeepers.count()
    
    print(f"Средний пас вратарей: {avg_passing:.1f}")
    print(f"Среднее видение вратарей: {avg_vision:.1f}")

if __name__ == "__main__":
    check_goalkeepers()