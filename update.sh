#!/usr/bin/env bash

# Copyright (c) 2024-2026 Vili and contributors.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}H4X-Tools Update Script${NC}"
echo -e "-- Made in Finland, by Vili.\n"

# Ensure user is in the correct directory
if [ ! -d ".git" ]; then
    echo -e "${RED}[!] Error: Run this script from the root of the cloned H4X-Tools repository.${NC}"
    exit 1
fi

read -r -p "Do you want to update H4XTools? (y/N) " answer
if [[ "$answer" =~ ^[yY](es)?$ ]]; then
    echo -e "\n${GREEN}[*] Fetching and pulling latest changes...${NC}"
    git fetch
    git pull

    echo -e "\n${GREEN}[+] Update downloaded successfully.${NC}"
    read -r -p "Do you want to run setup.sh now to rebuild the tool? (y/N) " run_setup
    if [[ "$run_setup" =~ ^[yY](es)?$ ]]; then
        bash setup.sh
    fi
else
    echo "Update cancelled."
fi
