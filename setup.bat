:: Copyright (c) 2024-2026 Vili and contributors.
@echo off
setlocal
cls

echo.
echo H4X-Tools Setup Script
echo.
echo -- Made in Finland, by Vili.
echo.

if not exist h4xtools.py (
    echo Error: Please run this script from the H4X-Tools project directory.
    pause
    exit /b 1
)

if not exist requirements.txt (
    echo Error: requirements.txt was not found.
    pause
    exit /b 1
)

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Error: Python 3 was not found.
    echo Install Python 3.10+ from https://www.python.org/downloads/ and run setup again.
    pause
    exit /b 1
)

echo Using Python command: %PYTHON_CMD%
echo.

echo Creating virtual environment...
if not exist .venv (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Existing .venv found, reusing it.
)

set "VENV_PYTHON=.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo Error: Virtual environment Python was not found at %VENV_PYTHON%.
    echo Delete .venv and run setup again.
    pause
    exit /b 1
)

echo.
echo Upgrading pip tooling...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo Error: Failed to upgrade pip tooling.
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo Virtual environment: .venv
echo Run H4X-Tools with: .venv\Scripts\python.exe h4xtools.py
echo Or activate the environment with: .venv\Scripts\activate.bat
echo.

set /p "RUN_NOW=Do you want to run H4X-Tools with Python now? (y/N) "
if /i "%RUN_NOW%"=="y" (
    "%VENV_PYTHON%" h4xtools.py
) else if /i "%RUN_NOW%"=="yes" (
    "%VENV_PYTHON%" h4xtools.py
)

endlocal
exit /b 0
