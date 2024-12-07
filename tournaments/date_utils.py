import calendar
from datetime import date
from django.utils import timezone

def get_next_season_dates():
    """
    Вычисляет даты начала и конца следующего сезона.
    Использует реальное количество дней в каждом месяце.
    Возвращает кортеж (start_date, end_date).
    """
    today = timezone.now().date()
    
    # Определяем начало сезона - первое число следующего месяца
    if today.day != 1:
        year = today.year
        month = today.month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        start_date = date(year, month, 1)
    else:
        # Если сегодня 1 число, начинаем сезон сегодня
        start_date = today

    # Определяем последний день месяца используя calendar.monthrange
    _, last_day = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date.replace(day=last_day)
    
    return start_date, end_date