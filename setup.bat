@echo off
cls
echo
echo     //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )
echo    //___ / //___/ /   \  /         / /    //   / / //   / / / /        ((
echo   / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\
echo  //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )
echo //    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /
echo.
echo ~~by Vili (https://github.com/v1li)
echo.
echo Installing dependencies in 3 seconds...
timeout /t 3 /nobreak > nul
pip3 install -r requirements.txt
echo.
echo.
echo Installing Maigret and Holehe in 3 seconds...
timeout /t 3 /nobreak > nul
pip3 install maigret holehe
timeout /t 1 /nobreak > nul
echo.
echo Done..!
echo.
echo Building H4XTools to a single executable in 3 seconds...
timeout /t 3 /nobreak > nul
python -m PyInstaller --onefile h4xtools.py
echo.
echo Done..!
echo Your H4XTools executable is located in the dist folder. You can now move it to your desired location.
echo.

set /p "input=Start H4XTools now? (y/n) -> "
if /i "%input%"=="y" (
    echo Starting H4XTools...
    timeout /t 1 /nobreak > nul
    start dist\h4xtools.exe
) else (
    echo Exiting...
    timeout /t 1 /nobreak > nul
)
exit
