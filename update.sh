#!/usr/bin/env bash

# Copyright (c) 2023. Vili and contributors.

clear

cat << "EOF"
    //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )
   //___ / //___/ /   \  /         / /    //   / / //   / / / /        ((
  / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\
 //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )
//    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /

~~by Vili (https://vili.dev)

EOF

echo
echo
echo "Make sure to run this in the directory that you cloned from GitHub!"
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
