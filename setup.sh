#!/usr/bin/env bash

# Copyright (c) 2023. Vili and contributors.

clear

cat << "EOF"

 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀
~~by Vili (https://vili.dev)

EOF

echo "Press CTRL+C to cancel."
echo
echo "Note that this script might ask for sudo password."
echo
echo "You may need to install python-devel package."
sleep 3

echo "Creating virtual environment..."
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

echo "Updating pip..."
sleep 1
pip3 install --upgrade pip

echo "Installing dependencies in 3 seconds..."
sleep 3

# Install dependencies
if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
else
    echo "python3-pip not installed, failed to install dependencies."
fi

sleep 1
echo "Building H4X-Tools to a single executable in 3 seconds..."
sleep 3

chmod +x h4xtools.py

if command -v pyinstaller >/dev/null 2>&1; then
    pyinstaller h4xtools.py --add-data "resources/*:resources" --onefile -F --clean
    sleep 1
    chmod +x dist/h4xtools
    sudo mv dist/h4xtools /usr/local/bin/
    rm h4xtools.spec
    rm -r build
    rm -r dist
    echo "Done! Type h4xtools in your terminal to start! OR Do you want to start H4XTools now? [y/n]"
    read -r answer
    if [ "$answer" = "y" ]; then
        h4xtools
    fi
else
    echo "pyinstaller not installed or not in PATH!"
