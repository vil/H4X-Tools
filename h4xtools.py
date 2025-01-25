#!/usr/bin/env python3

"""
 Copyright (c) 2023-2025. Vili and contributors.

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

import os, time, socket
from colorama import Fore, Style
from helper import printer, handles

VERSION = "0.3.1"

def internet_check() -> None:
    try:
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
    except OSError:
        printer.warning("Internet Connection is Unavailable..!")

def print_banner() -> None:
    print(Fore.LIGHTBLACK_EX + f"""                              
 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ · 
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀. 
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀ 
{Style.RESET_ALL}v{VERSION} / Vili (@vil) / https://vili.dev 
    """)

def help() -> None:
    print(Fore.LIGHTCYAN_EX)
    printer.nonprefix(f"""
H4X-Tools v{VERSION}, a toolkit for scraping, OSINT and more.

Repository link : https://github.com/vil/h4x-tools

Made in Finland, with love.


Name          Desc
---------     ----------
Ig Scrape : Scrapes information from IG accounts.
Web Search : Searches the internet for the given query.
Phone Lookup : Looks up a phone number and returns information about it.
Ip Lookup : Looks up an IP/domain address and returns information about it.
Port Scanner : Scans for open ports in a given IP/domain address.
Username Search : Tries to find a given username from many different websites.
Cybercrime int : Searches if given email/domain has been compromised and leaked.
Email Search : Efficiently finds registered accounts from a given email.
Webhook Spammer : Spams messages to a discord webhook.
WhoIs Lookup : Looks up a domain and returns information about it.
SMS Bomber : Spams messages to a given mobile number. (Works poorly and only for US numbers)
Fake Info Generator : Generates fake information using Faker.
Web Scrape : Scrapes links from a given url.
Wi-Fi Finder : Scans for nearby Wi-Fi networks.
Wi-Fi Vault : Scans for locally saved Wi-Fi passwords.
Dir Buster : Bruteforce directories on a website.
Local Users : Enumerates local user accounts on the current machine.
Caesar Cipher : Cipher/decipher/bruteforce a message using the Caesar's code.
BaseXX : Encodes/decodes a message using Base64/32/16.
Help : Shows the help message.

You can close the toolkit with the commands quit, q, kill and exit.

This toolkit is under the GNU General Public License, version 3, and is made by Vili.
    """)


def print_menu() -> None:
    max_option_length = max(len(value.__name__.replace('handle_', '').replace('_', ' ').title()) for value in MENU_OPTIONS.values())

    for i, (key, value) in enumerate(MENU_OPTIONS.items(), start=1):
        option_name = value.__name__.replace('handle_', '').replace('_', ' ').title()
        print(f"{Fore.LIGHTGREEN_EX}[{key.zfill(2)}]{Style.RESET_ALL} {option_name.ljust(max_option_length)}", end='')

        if i % 2 == 0:
            print()
        else:
            print(" " * 4, end='')

    print("\n")
    print(f"Type {Style.BRIGHT}?{Style.RESET_ALL} for help.")
    print(f"Type {Style.BRIGHT}exit{Style.RESET_ALL} to close the toolkit...")

MENU_OPTIONS = {
    "1": handles.handle_ig_scrape,
    "2": handles.handle_web_search,
    "3": handles.handle_phone_lookup,
    "4": handles.handle_ip_lookup,
    "5": handles.handle_username_search,
    "6": handles.handle_email_search,
    "7": handles.handle_cybercrime_int,
    "8": handles.handle_port_scanner,
    "9": handles.handle_webhook_spammer,
    "10": handles.handle_whois_lookup,
    "11": handles.handle_sms_bomber,
    "12": handles.handle_fake_info_generator,
    "13": handles.handle_web_scrape,
    "14": handles.handle_wifi_finder,
    "15": handles.handle_wifi_vault,
    "16": handles.handle_dir_buster,
    "17": handles.handle_local_users,
    "18": handles.handle_caesar_cipher,
    "19": handles.handle_basexx
}

def main() -> None:
    internet_check()
    time.sleep(0.5)

    if os.name == "nt":
        printer.warning("Windows system detected..! Expect issues...")
        time.sleep(1)

    while True:
        print_banner()
        time.sleep(1)
        print_menu()
        user_input = printer.inp(f"Tool to execute : \t")

        if user_input.lower() in {"quit", "exit", "q", "kill"}:
            """
            Kills the program.
            """
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            time.sleep(0.5)
            break

        if user_input.lower() == "?":
            help()
            time.sleep(3)

        if user_input in MENU_OPTIONS:
            try:
                MENU_OPTIONS[user_input]()  # Call the corresponding function based on the selected option
            except KeyboardInterrupt:
                printer.warning("Cancelled..!")
            time.sleep(3)  # Sleep so the user has time to see results.
        else:
            printer.error("Invalid option!")
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        printer.warning("Quitting... Goodbye!")
        print(Style.RESET_ALL)
        exit(1)
