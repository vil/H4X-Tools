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
pip3 install -r requirements.txt
sleep 1
echo Making H4XTools into a linux command...
pyinstaller h4xtools.py --onefile
sudo cp -i dist/h4xtools /usr/local/bin/
sudo chmod +x /usr/local/bin/h4xtools 
echo Done! Type h4xtools in your terminal to start! OR Do you want to start H4XTools now? [y/n]
read answer
if [ "$answer" = "y" ]; then
    h4xtools
fi