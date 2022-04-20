@ECHO OFF
:start
cls
echo Installing dependencies in 3 seconds...
timeout /t 3 /nobreak
pip3 install -r requirements.txt
timeout /t 1 /nobreak
set /p input= Start H4XTools now? (y/n)
if %input%==y python h4xtools.py
else echo Exiting...
timeout /t 1 /nobreak
:exit