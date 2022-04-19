#!/usr/bin/env bash

clear
echo Installing dependencies in 3 seconds...
sleep 3
pip install -r requirements.txt
sleep 1
echo Done! Do you want to start H4XTools now? [y/n]
read answer
if [ "$answer" = "y" ]; then
    python3 h4xtools.py
fi