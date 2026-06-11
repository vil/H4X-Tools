#!/usr/bin/env bash

# Copyright (c) 2024-2026 Vili and contributors.

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}H4X-Tools Setup Script${NC}"
echo -e "-- Made in Finland, by Vili (@vil).\n"

if [ ! -f "h4xtools.py" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[!] Please run this script from the H4X-Tools project directory.${NC}"
    exit 1
fi

echo -e "${GREEN}[*] Checking system dependencies...${NC}"
if command -v apt-get >/dev/null 2>&1; then
    echo "Detected Debian/Ubuntu-based system."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential git
elif command -v dnf >/dev/null 2>&1; then
    echo "Detected Fedora/RHEL-based system."
    sudo dnf install -y python3 python3-pip python3-devel gcc git
elif command -v pacman >/dev/null 2>&1; then
    echo "Detected Arch-based system."
    sudo pacman -Sy --noconfirm python python-pip python-virtualenv base-devel git
elif command -v zypper >/dev/null 2>&1; then
    echo "Detected openSUSE-based system."
    sudo zypper install -y python3 python3-pip python3-devel gcc git
else
    echo -e "${YELLOW}[!] Unsupported or unrecognised package manager.${NC}"
    echo "Please make sure Python 3, pip, venv, git, and build tools are installed."
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}[!] python3 was not found. Install Python 3.10+ and run setup again.${NC}"
    exit 1
fi

echo -e "\n${GREEN}[*] Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
else
    echo "Existing .venv found, reusing it."
fi

VENV_PYTHON=".venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    echo -e "${RED}[!] Virtual environment Python was not found at $VENV_PYTHON.${NC}"
    echo "Delete .venv and run setup again."
    exit 1
fi

echo -e "\n${GREEN}[*] Upgrading pip tooling...${NC}"
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

echo -e "\n${GREEN}[*] Installing Python dependencies...${NC}"
"$VENV_PYTHON" -m pip install -r requirements.txt

echo -e "\n${GREEN}[+] Setup complete!${NC}"
echo "Virtual environment: .venv"
echo "Run H4X-Tools with: .venv/bin/python h4xtools.py"
echo "Or activate the environment with: source .venv/bin/activate"

echo ""
read -r -p "Do you want to run H4X-Tools now? (y/N) " answer
if [[ "$answer" =~ ^[yY](es)?$ ]]; then
    "$VENV_PYTHON" h4xtools.py
fi
