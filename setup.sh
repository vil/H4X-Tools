#!/usr/bin/env bash

# Copyright (c) 2024-2026 Vili and contributors.

# Stop script execution if any command fails
set -e

# Setup basic colors for better terminal readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}H4X-Tools Setup Script${NC}"
echo -e "-- Made in Finland, by Vili (@vil).\n"

# 1. Install OS Dependencies based on the package manager
echo -e "${GREEN}[*] Checking and installing system dependencies...${NC}"
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
    echo -e "${YELLOW}[!] Unsupported or unrecognised package manager. Please ensure Python3, pip, venv, and dev tools are installed manually.${NC}"
fi

# 2. Virtual Environment
echo -e "\n${GREEN}[*] Creating virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependencies
echo -e "\n${GREEN}[*] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller # Ensures PyInstaller is strictly in the venv

# 4. Build Executable
echo -e "\n${GREEN}[*] Building H4X-Tools to a single executable...${NC}"
pyinstaller h4xtools.py --add-data "resources/*:resources" --onefile -F --clean

# 5. Setup Binary in User Local Bin
echo -e "\n${GREEN}[*] Installing executable to ~/.local/bin...${NC}"
mkdir -p "$HOME/.local/bin"
mv dist/h4xtools "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/h4xtools"

# 6. Cleanup
echo -e "\n${GREEN}[*] Cleaning up build artifacts...${NC}"
rm -f h4xtools.spec
rm -rf build/ dist/

echo -e "\n${GREEN}[+] Setup complete!${NC}"

# Check if ~/.local/bin is actually in the user's PATH variable
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}WARNING: $HOME/.local/bin is not in your PATH.${NC}"
    echo "To run 'h4xtools' globally, add this line to your ~/.bashrc or ~/.zshrc:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo "Alternatively, you can start it right now using its direct path."
fi

echo ""
read -r -p "Do you want to start H4XTools now? (y/N) " answer
if [[ "$answer" =~ ^[yY](es)?$ ]]; then
    "$HOME/.local/bin/h4xtools"
fi
