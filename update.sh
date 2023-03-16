#!/usr/bin/env sh

clear
echo """

██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░

by Vili (https://github.com/v1li)
"""
echo
echo
echo Make sure to run this in the main directory!
echo
echo Do you want to update H4XTools? [y/n]
read answer
if [ "$answer" = "y" ]; then
    git fetch
    git pull
fi
echo Run setup.sh to apply changes. Do it now? [y/n]
read answer
if [ "$answer" = "y" ]; then
    sh setup.sh
fi
