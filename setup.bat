:: Copyright (c) 2024. Vili and contributors.
@echo off
cls
echo.
echo H4X-Tools Setup Script
echo.
echo ~~by Vili (https://vili.dev)
echo.
echo Installing dependencies in 3 seconds...
timeout /t 3 /nobreak > nul
python -m pip install -r requirements.txt
echo.
timeout /t 1 /nobreak > nul
echo.
echo Done..!
echo.
echo Building H4X-Tools to a single executable in 3 seconds...
timeout /t 3 /nobreak > nul
python -m PyInstaller h4xtools.py --add-data "resources\*;resources" --onefile -F --clean
echo.
echo Done..!
echo Your H4X-Tools executable is located in the 'dist' folder. You can now move it to your desired location.
echo.
echo OR you can start H4X-Tools with python by typing 'python h4xtools.py' in the terminal.

set /p "input=Open 'dist' folder now? (y/n) -> "
if /i "%input%"=="y" (
    echo Opening up 'dist'.
    timeout /t 1 /nobreak > nul
    start dist\.
) else (
    echo Exiting...
    timeout /t 1 /nobreak > nul
)
exit
