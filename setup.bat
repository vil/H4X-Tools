:: Copyright (c) 2024-2025 Vili and contributors.
@echo off
cls
echo.
echo H4X-Tools Setup Script
echo.
echo -- Made in Finland, by Vili.
echo.

:: Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)
echo Done.

:: Build executable
echo Building H4X-Tools to a single executable...
python -m PyInstaller h4xtools.py --add-data "resources\*;resources" --onefile -F --clean
if %errorlevel% neq 0 (
    echo Error: Failed to build executable.
    pause
    exit /b 1
)
echo Done.

:: Open dist folder
echo Your H4X-Tools executable is located in the 'dist' folder. You can now move it to your desired location.
echo OR you can start H4X-Tools with python by typing 'python h4xtools.py' in the terminal.
echo.
set /p "input=Open 'dist' folder now? (y/N) -> "
if /i "%input%"=="y" (
    echo Opening up 'dist'.
    start dist\.
) else (
    echo Exiting...
)
pause
exit /b 0
