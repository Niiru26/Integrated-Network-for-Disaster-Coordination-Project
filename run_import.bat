@echo off
cls
echo ========================================
echo    I.N.D.C. PROJECT - DATA IMPORT TOOL
echo    Integrated Network for Disaster Coordination
echo ========================================
echo.
echo This will import Excel data to your database
echo.
echo Current folder: %CD%
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause > nul

cd /d C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\01_Scripts
echo.
echo Running import script...
echo ------------------------
python import_all.py

echo.
echo ========================================
echo Import complete! Press any key to exit...
echo ========================================
pause > nul