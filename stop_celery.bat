@echo off
color 0C
chcp 65001 > nul

echo [%date% %time%] Stopping Celery processes...
echo =====================================

taskkill /F /FI "WindowTitle eq Celery Worker*" /T
taskkill /F /FI "WindowTitle eq Celery Beat*" /T

echo.
echo [%date% %time%] All processes stopped.
echo Press any key to exit...
pause > nul