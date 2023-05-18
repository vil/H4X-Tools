@echo off
:start
cls
echo "    //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )"
echo "   //___ / //___/ /   \  /         / /    //   / / //   / / / /        (("
echo "  / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\"
echo " //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )"
echo "//    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /"
echo
echo "by Vili (https://github.com/v1li)"
echo
echo "Installing dependencies in 3 seconds..."
timeout /t 3 /nobreak
pip3 install -r requirements.txt
echo
echo
echo "Installing Maigret and Holehe in 3 seconds..."
timeout /t 3 /nobreak
pip3 install maigret holehe
timeout /t 1 /nobreak
echo
echo "Done!"
set /p input= "Start H4XTools now? (y/n) -> "
if %input%==y python h4xtools.py
else echo "Exiting..."
timeout /t 1 /nobreak
:exit