#!/usr/bin/env sh

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
echo "Make sure to run this in the main directory if this script cant find it automatically."
echo
echo "Checking for H4X-Tools directory location..."
HOME_DIR=$(eval echo "~")
H4XTOOLS_FILE="$HOME_DIR/.h4xtools"

sleep 1

if [ -f "$H4XTOOLS_FILE" ]; then
    source "$H4XTOOLS_FILE"
    echo "H4X-Tools directory location found: $H4XTOOLS_DIR"
    echo
    echo "Do you want to update H4XTools? [y/n]"
    read -r answer
    if [ "$answer" = "y" ]; then
        cd "$H4XTOOLS_DIR" || exit
        git fetch
        git pull
    fi
else
    echo "H4X-Tools directory location not found. Update failed."
fi

echo "Run setup.sh to apply changes. Do it now? [y/n]"
read -r answer
if [ "$answer" = "y" ]; then
    sh setup.sh
fi
