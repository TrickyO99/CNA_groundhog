@echo off
cd /d "%~dp0"
echo Running groundhog with the sample data in utils\temperatures, period=7...
python src\groundhog.py 7 < utils\temperatures
echo.
echo (Try other periods: Run.bat calls "groundhog.py 7"; from a terminal you can
echo  use any period, e.g. "python src\groundhog.py 14 < utils\temperatures")
echo.
pause
