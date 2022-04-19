@ECHO OFF
:start
cls
echo 'Installing dependencies in 3 seconds...'
timeout /t 3
pip install -r requirements.txt
timeout /t 1
set /p input= y/n
if %input%==y python h4xtools.py
else echo 'Exiting...'
timeout /t 1
:exit