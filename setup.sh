#!/usr/bin/env sh

clear
echo """

██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░

by Vp (https://github.com/herravp)
"""

echo Installing dependencies in 3 seconds...
sleep 3

if pip3 --version; then
    pip3 install -r requirements.txt
else
    echo python3-pip not installed, failed to install dependencies.
fi

sleep 1
echo Making H4XTools into a linux command...
chmod +x h4xtools.py

if pyinstaller --version; then
    pyinstaller h4xtools.py --onefile -F
    sleep 1
    cd dist
    chmod +x h4xtools
    sudo mv h4xtools /usr/local/bin/
    cd -
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
fi

