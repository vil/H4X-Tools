#!/usr/bin/env bash

clear

cat << "EOF"
    //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )
   //___ / //___/ /   \  /         / /    //   / / //   / / / /        ((
  / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\
 //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )
//    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /

~~by Vili (https://github.com/v1li)

EOF

echo
echo
echo "Make sure to run this in the main directory!"
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
