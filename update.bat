:: Copyright (c) 2024. Vili and contributors.
@echo off
cls
echo.
echo H4X-Tools Update Script
echo.
echo ~~by Vili (https://vili.dev)
echo.
echo Make sure you run this in the root project directory!
echo.

set /p "input=Do you want to continue and update H4X-Tools? (y/n) "

if /i "%input%"=="y" (
    echo Updating...
    git fetch
    git pull
    echo Updating complete. Rebuilding setup...
    start setup.bat
) else (
    echo Exiting...
)
exit