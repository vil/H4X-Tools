:: Copyright (c) 2023. Vili and contributors.
@echo off
cls
echo.
echo ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·
echo ██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.
echo ██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
echo ██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
echo ▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀
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

set /p "input=Start H4X-Tools now? (y/n) -> "
if /i "%input%"=="y" (
    echo Starting H4XTools...
    timeout /t 1 /nobreak > nul
    start dist\h4xtools.exe
) else (
    echo Exiting...
    timeout /t 1 /nobreak > nul
)
exit
