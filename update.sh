#!/usr/bin/env bash

# Copyright (c) 2024. Vili and contributors.

clear

echo "H4X-Tools Update Script"
echo
echo "~~by Vili (https://vili.dev)"
echo
echo "Make sure to run this in the root project directory!"

read -r -p "Do you want to update H4XTools? (y/n) " answer
if [[ $answer == "y" ||  $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]; then
    git fetch
    git pull
    echo "Update complete. Run setup.sh to apply changes."
    read -r -p "Do it now? (y/n) " answer
    if [[ $answer == "y" ||  $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]; then
        bash setup.sh
    fi
else
    echo "Update cancelled."
fi