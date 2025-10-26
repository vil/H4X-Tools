#!/usr/bin/env bash

# Copyright (c) 2024-2025 Vili and contributors.

clear

echo "H4X-Tools Setup Script"
echo
echo "-- Made in Finland, by Vili."
echo
echo "You may need to install 'python-devel' packages."

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "python3-pip not installed, failed to install dependencies."
    exit 1
fi

# Build H4X-Tools to a single executable
echo "Building H4X-Tools to a single executable..."
if command -v pyinstaller >/dev/null 2>&1; then
    pyinstaller h4xtools.py --add-data "resources/*:resources" --onefile -F --clean
    chmod +x dist/h4xtools
    if [ -d "$HOME/.local/bin" ]; then
        mv dist/h4xtools "$HOME/.local/bin"
    else
        mkdir "$HOME/.local/bin"
        mv dist/h4xtools "$HOME/.local/bin"
    fi
    rm h4xtools.spec
    rm -r build
    rm -r dist
    echo "Done! Type h4xtools in your terminal to start!"
    read -r -p "Do you want to start H4XTools now? (y/N) " answer
    if [[ $answer == "y" ||  $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]; then
        h4xtools
    fi
else
    echo "pyinstaller not installed or not in PATH!"
    exit 1
fi
