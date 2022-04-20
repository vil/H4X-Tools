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

if [ -e  /usr/lib/sudo ];then
  if [ -e /usr/bin/apt-get ];then
    if [ ! -e /usr/bin/python3 ];then
       sudo apt-get update
       sudo apt-get upgrade -y
       sudo apt-get install python -y
       sudo apt-get install python3 -y
       sudo apt-get install python3-pip -y
       sudo apt-get install git -y
     fi
  fi
else
 if [ -d /usr/bin ];then
    if [ -e /usr/bin/apt-get ];then
      if [ ! -e /usr/bin/python3 ];then
       apt-get update
       apt-get upgrade -y
       apt-get install python -y
       apt-get install python3 -y
       apt-get install python3-pip -y
       apt-get install git -y
      fi
    fi
  fi
fi
if [ -d /data/data/com.termux/files/usr/bin ]; then
  if [ ! -e /data/data/com.termux/files/usr/bin/python3 ];then
    pkg update
    pkg upgrade -y
    pkg install python -y
    pkg install python3 -y
    pkg install python3-pip -y
    pkg install git -y
  fi
fi
if [ -e  /usr/lib/sudo ];then
  if [ -e /usr/bin/dnf ];then
    if [ ! -e /usr/bin/python3 ];then
       sudo dnf update
       sudo dnf upgrade -y
       sudo dnf install python -y
       sudo dnf install python3 -y
       sudo dnf install python3-pip -y
       sudo dnf install git -y
     fi
  fi
else
  if [ -d /usr/bin ];then
    if [ -e /usr/bin/dnf ];then
      if [ ! -e /usr/bin/python3 ];then
       dnf update
       dnf upgrade -y
       dnf install python -y
       dnf install python3 -y
       dnf install python3-pip -y
       dnf install git -y
      fi
    fi
  fi
fi
if [ -e  /usr/local/bin/brew ];then
  if [ ! -e /usr/local/bin/python3 ];then
     brew install python -y
     brew install python3 -y
     brew install python3-pip -y
     brew install git -y
   fi
fi
if [ -e  /usr/local/bin/brew ];then
  if [ ! -e /usr/local/bin/python ];then
     brew install python -y
     brew install python3 -y
     brew install python3-pip -y
     brew install git -y
   fi
fi
if [ -e  /usr/bin/apk ];then
  if [ ! -e /usr/bin/python ];then
     apk install python -y
     apk install python3 -y
     apk install python3-pip -y
     apk install git -y
   fi
fi
if [ -e  /usr/bin/apk ];then
  if [ ! -e /usr/bin/python3 ];then
     apk install python -y
     apk install python3 -y
     apk install python3-pip -y
     apk install git -y
   fi
fi
sleep 1

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