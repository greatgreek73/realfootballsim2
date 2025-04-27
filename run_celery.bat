@echo off
title Celery Processes + Flower
color 0A
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo [%date% %time%] Starting Celery processes...
echo =====================================

:: Активация виртуального окружения
call venv310\Scripts\activate.bat

:: 1) Daphne (зелёное)
echo [%date% %time%] Starting Daphne Server...
start "Daphne Server" cmd /k ^
 "chcp 65001>nul && set PYTHONIOENCODING=utf-8 && color 0A && daphne -b 0.0.0.0 -p 8000 realfootballsim.asgi:application"

timeout /t 2 > nul

:: 2) Celery worker (синее)
echo [%date% %time%] Starting Celery Worker...
start "Celery Worker" cmd /k ^
 "chcp 65001>nul && set PYTHONIOENCODING=utf-8 && color 0B && celery -A realfootballsim worker --pool=solo -l info"

timeout /t 2 > nul

:: 3) Celery beat (красное)
echo [%date% %time%] Starting Celery Beat...
start "Celery Beat" cmd /k ^
 "chcp 65001>nul && set PYTHONIOENCODING=utf-8 && color 0C && celery -A realfootballsim beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

timeout /t 2 > nul

:: 4) Flower (желтое)
echo [%date% %time%] Starting Flower...
start "Flower" cmd /k ^
 "chcp 65001>nul && set PYTHONIOENCODING=utf-8 && color 0E && celery -A realfootballsim flower --address=127.0.0.1 --port=5555"

echo.
echo [%date% %time%] All processes started!
echo.
echo Window colors:
echo - Green : Daphne
echo - Blue  : Celery Worker
echo - Red   : Celery Beat
echo - Yellow: Flower (UI http://127.0.0.1:5555)
echo.
echo Press any key to stop all processes...
echo =====================================
pause > nul

:: -------- Остановка -------
echo.
echo [%date% %time%] Stopping processes...
taskkill /F /FI "WindowTitle eq Daphne Server*" /T
taskkill /F /FI "WindowTitle eq Celery Worker*" /T
taskkill /F /FI "WindowTitle eq Celery Beat*"   /T
taskkill /F /FI "WindowTitle eq Flower*"        /T

echo.
echo [%date% %time%] All processes stopped.
echo Press any key to exit...
pause > nul
