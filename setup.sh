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

echo "Installing dependencies in 3 seconds..."
echo "Press CTRL+C to cancel."
echo
echo "Note that this script might ask for sudo password."
sleep 3

if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
    echo "Installing maigret and holehe for email and username search..."
    sleep 2
    pip3 install maigret holehe
else
    echo "python3-pip not installed, failed to install dependencies."
fi

sleep 1
echo "Making H4XTools into a Linux command..."
sleep 1

chmod +x h4xtools.py

if command -v pyinstaller >/dev/null 2>&1; then
    pyinstaller h4xtools.py --onefile -F
    sleep 1
    chmod +x dist/h4xtools
    sudo mv dist/h4xtools /usr/local/bin/
    rm h4xtools.spec
    rm -r build
    rm -r dist
    echo "Done! Type h4xtools in your terminal to start! OR Do you want to start H4XTools now? [y/n]"
    read -r answer
    if [ "$answer" = "y" ]; then
        h4xtools
    fi
else
    echo "pyinstaller not installed or not in PATH!"
    echo "Try running the script as sudo."
fi