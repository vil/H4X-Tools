#!/usr/bin/env sh

clear
echo """

██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░

by Vili (https://github.com/v1li)
"""

echo Installing dependencies in 3 seconds...
sleep 3

if pip3 --version; then
    pip3 install -r requirements.txt
else
    echo python3-pip not installed, failed to install dependencies.
fi

sleep 1
echo Making H4XTools into a linux command... Might ask for sudo password.
sleep 1

chmod +x h4xtools.py

if pyinstaller --version; then
    pyinstaller h4xtools.py --onefile -F
    sleep 1
    chmod +x dist/h4xtools
    sudo mv dist/h4xtools /usr/local/bin/
    rm h4xtools.spec
    rm build -r
    rm dist -r
    echo Done! Type h4xtools in your terminal to start! OR Do you want to start H4XTools now? [y/n]
    read answer
    if [ "$answer" = "y" ]; then
        h4xtools
    fi
else
    echo pyinstaller not installed or in path!
    echo This can be fixed by running: sudo pip3 install pyinstaller
fi

