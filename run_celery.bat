@echo off
title Celery Processes

:: Настраиваем цвета и кодировку
color 0A
:: Устанавливаем UTF-8 кодировку для консоли
chcp 65001 > nul
:: Устанавливаем переменную окружения для Python
set PYTHONIOENCODING=utf-8

echo [%date% %time%] Starting Celery processes...
echo =====================================

:: Активация виртуального окружения
call venv310\Scripts\activate.bat

:: Запускаем Redis в отдельном окне
echo [%date% %time%] Starting Redis Server...
start "Redis Server" cmd /k "color 0F && \"C:\Program Files\Redis\redis-server.exe\""
timeout /t 2 > nul


:: Запускаем Daphne в отдельном окне
echo [%date% %time%] Starting Daphne Server...
start "Daphne Server" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && color 0A && daphne -b 0.0.0.0 -p 8000 realfootballsim.asgi:application"

:: Небольшая пауза между запусками
timeout /t 2 > nul

:: Запускаем worker в отдельном окне без перенаправления в файл
echo [%date% %time%] Starting Celery Worker...
start "Celery Worker" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && color 0B && celery -A realfootballsim worker --pool=solo -l info"

:: Небольшая пауза между запусками
timeout /t 2 > nul

:: Запускаем beat в отдельном окне без перенаправления в файл
echo [%date% %time%] Starting Celery Beat...
start "Celery Beat" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && color 0C && celery -A realfootballsim beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo.
echo [%date% %time%] All processes started!
echo.
echo Window colors:
echo - Green: Daphne Server
echo - Blue: Celery Worker
echo - Red: Celery Beat
echo.
echo Press any key to stop all processes...
echo =====================================

pause > nul

:: Останавливаем процессы
echo.
echo [%date% %time%] Stopping processes...
taskkill /F /FI "WindowTitle eq Daphne Server*" /T
taskkill /F /FI "WindowTitle eq Celery Worker*" /T
taskkill /F /FI "WindowTitle eq Celery Beat*" /T

echo.
echo [%date% %time%] All processes stopped.
echo Press any key to exit...
pause > nul
