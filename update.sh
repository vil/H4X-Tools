#!/usr/bin/env bash

# Copyright (c) 2023. Vili and contributors.

clear

echo "H4X-Tools Update Script"
echo
echo "~~by Vili (https://vili.dev)"
echo
echo "Make sure to run this in the root project directory!"
echo
echo "Do you want to update H4XTools? [y/n]"
read -r answer
if [ "$answer" = "y" ]; then
    git fetch
    git pull
fi
echo "Run setup.sh to apply changes. Do it now? [y/n]"
read -r answer
if [ "$answer" = "y" ]; then
    bash setup.sh
fi
