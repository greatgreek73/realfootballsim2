@echo off
title Celery Processes

:: Настраиваем цвета и кодировку
color 0A
chcp 65001 > nul

echo [%date% %time%] Starting Celery processes...
echo =====================================

:: Активация виртуального окружения
call venv310\Scripts\activate.bat

:: Запускаем worker в отдельном окне без перенаправления в файл
echo [%date% %time%] Starting Celery Worker...
start "Celery Worker" cmd /k "color 0B && celery -A realfootballsim worker --pool=solo -l info"

:: Небольшая пауза между запусками
timeout /t 2 > nul

:: Запускаем beat в отдельном окне без перенаправления в файл
echo [%date% %time%] Starting Celery Beat...
start "Celery Beat" cmd /k "color 0C && celery -A realfootballsim beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo.
echo [%date% %time%] All processes started!
echo.
echo Window colors:
echo - Blue: Celery Worker
echo - Red: Celery Beat
echo.
echo Press any key to stop all processes...
echo =====================================

pause > nul

:: Останавливаем процессы
echo.
echo [%date% %time%] Stopping processes...
taskkill /F /FI "WindowTitle eq Celery Worker*" /T
taskkill /F /FI "WindowTitle eq Celery Beat*" /T

echo.
echo [%date% %time%] All processes stopped.
echo Press any key to exit...
pause > nul