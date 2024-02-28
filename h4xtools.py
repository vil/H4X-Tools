#!/usr/bin/env python3

"""
 Copyright (c) 2024. Vili and contributors.

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import os
import time
import socket
from colorama import Fore
from helper import printer, handles


if os.name == "nt":
    os.system("cls")
    os.system("title H4X-Tools")
if os.name == "posix":
    os.system("clear")

VERSION = "0.2.15+"


def internet_check() -> None:
    """
    Checks if the internet connection is available.

    :return: None
    """
    try:
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
    except OSError:
        printer.warning("Internet Connection is Unavailable..!")


def print_banner() -> None:
    """
    Prints the banner of H4X-Tools.
    """
    print(Fore.CYAN + f"""
 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ · 
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀. 
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀ v{VERSION} 
~~by Vili (https://vili.dev)
    """)


def about() -> None:
    """
    Prints the about text.
    """
    print(Fore.GREEN)
    printer.nonprefix(f"""
H4X-Tools, toolkit for scraping, OSINT and more.
Completely open source and free to use! Feel free to contribute.
Repo: https://github.com/vil/h4x-tools
NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DON'T USE IT ILLEGALLY!
Version: {VERSION}
    """)


def donate() -> None:
    """
    Prints the donate text.
    """
    printer.nonprefix(f"""{Fore.GREEN}
If you want to support me and my work, you can donate to these addresses: \n
| BCH: qp58pmwsfq4rp0vvafjrj2uenp8edmftycvvh8wmlg
| BTC: bc1qwgeuvc25g4hrylmgcup4yzavt5tl8pk93auj34
| ETH: 0x4433D6d7d31F38c63E0e6eA31Ffac2125B618142
| XMR: 47RTtA7b8dgQmd9dDYYTUrhsrXzdUvckLGqvZoBCwrchRdky1fLmzexL3esTNrTMstJiafnhDacsXi8UnS1AXACNKkNzv71
Or support me on GitHub: https://github.com/sponsors/vil
  
Every single donation is appreciated! <3
    """)


def print_menu() -> None:
    """
    Prints the main menu of H4X-Tools.
    """
    max_option_length = max(len(value.__name__.replace('handle_', '').replace('_', ' ').title()) for value in MENU_OPTIONS.values())

    for i, (key, value) in enumerate(MENU_OPTIONS.items(), start=1):
        option_name = value.__name__.replace('handle_', '').replace('_', ' ').title()
        print(f"[{key}] {option_name.ljust(max_option_length)}", end='\t')

        # Break line every two options or at the end
        if i % 2 == 0 or i == len(MENU_OPTIONS):
            print()

    print("\n")


MENU_OPTIONS = {
    "1": handles.handle_ig_scrape,
    "2": handles.handle_web_search,
    "3": handles.handle_phone_lookup,
    "4": handles.handle_ip_lookup,
    "5": handles.handle_username_search,
    "6": handles.handle_email_search,
    "7": handles.handle_port_scanner,
    "8": handles.handle_webhook_spammer,
    "9": handles.handle_whois_lookup,
    "10": handles.handle_sms_bomber,
    "11": handles.handle_fake_info_generator,
    "12": handles.handle_web_scrape,
    "13": handles.handle_wifi_finder,
    "14": handles.handle_wifi_password_getter,
    "15": handles.handle_dir_buster,
    "16": handles.handle_local_accounts_getter,
    "17": handles.handle_caesar_cipher,
    "18": handles.handle_basexx,
    "19": about,
    "20": donate,
    "21": handles.handle_exit
}


def main() -> None:
    """
    Main function.
    """
    internet_check()
    time.sleep(0.5)

    if os.name == "nt":
        printer.warning("Windows system detected..! Expect issues...")
        time.sleep(1)

    while True:
        print_banner()
        time.sleep(1)
        print_menu()
        user_input = input("[$] Select your option ~> \t")

        # Check if the user wants to exit
        if user_input.lower() in {"quit", "exit", "q", "kill"}:
            handles.handle_exit()

        if user_input in MENU_OPTIONS:
            MENU_OPTIONS[user_input]()  # Call the corresponding function based on the selected option
            time.sleep(3)  # Sleep so the user has time to see results.
        else:
            printer.error("Invalid option!")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
