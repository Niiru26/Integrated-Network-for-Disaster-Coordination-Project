@echo off
cls
echo ========================================
echo    I.N.D.C. PROJECT - CONNECTION TEST
echo    Integrated Network for Disaster Coordination
echo ========================================
echo.
echo Testing database connection...
echo --------------------------------
cd /d C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\01_Scripts
python test_connection.py

echo.
echo ========================================
echo Press any key to exit...
echo ========================================
pause > nul