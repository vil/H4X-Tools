#!/usr/bin/env python3

"""
 Copyright (c) 2023. Vili and contributors.

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
from colorama import Fore
import socket
import requests
from getpass import getpass
from utils import (
    email_search,
    search_username,
    ig_scrape,
    whois_lookup,
    webhook_spammer,
    port_scanner,
    ip_lookup,
    phonenumber_lookup,
    websearch,
    smsbomber,
    web_scrape,
    wifi_finder,
    wifi_password_getter,
    fake_info_generator,
    dirbuster,
    local_accounts_getter,
    caesar_cipher,
    basexx
)
from helper import printer, url_helper

if os.name == "nt":
    os.system("cls")
    os.system("title H4X-Tools")
if os.name == "posix":
    os.system("clear")

version = "0.2.14b"


def internet_check():
    """
    Checks if the internet connection is available.

    :return: None
    """
    try:
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
        return None
    except OSError:
        printer.warning("Internet Connection is Unavailable..!")
        return None


def version_check():
    """
    Checks the version from an external url and returns it.

    :return: version
    """
    path = "h4xtools/version.txt"
    try:
        r = url_helper.read_content(path)
        return r
    except requests.exceptions.ConnectionError:
        printer.error("Failed to check the version..!")


def print_banner():
    """
    Prints the banner of H4X-Tools.
    """
    print(Fore.CYAN + f"""
    //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )
   //___ / //___/ /   \  /         / /    //   / / //   / / / /        ((
  / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\
 //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )
//    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /  
v{version} ~~by Vili (https://vili.dev)
    """)


def about():
    """
    Prints the about text.
    """
    print(Fore.GREEN)
    printer.nonprefix(f"H4X-Tools, toolkit for scraping, OSINT and more.\n")
    printer.nonprefix(f"Completely open source and free to use! Feel free to contribute.\n")
    printer.nonprefix(f"Repo: https://github.com/v1li/h4x-tools\n")
    printer.nonprefix(f"NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")


def donate():
    """
    Prints the donate text.
    """
    printer.nonprefix(f"""{Fore.GREEN}
If you want to support me and my work, you can donate to these addresses: \n
| BCH: bitcoincash:qp58pmwsfq4rp0vvafjrj2uenp8edmftycvvh8wmlg
| BTC: bc1qwgeuvc25g4hrylmgcup4yzavt5tl8pk93auj34
| ETH: 0x4433D6d7d31F38c63E0e6eA31Ffac2125B618142
| XMR: 46jxBecqTunhWAitoBvQGaGUF8sZ3LmvuQzFzmFQZyAAWydLbTVnu4n2n6SXMkZTYhff4V2oGLBF2KgipLjMBgQ8HJswdXY
Or support me on GitHub: https://github.com/sponsors/v1li

Every single donation is appreciated! <3
            """)


def print_menu():
    """
    Prints the main menu of H4X-Tools.
    """
    max_option_length = max(len(value.__name__.replace('handle_', '').replace('_', ' ').title()) for value in menu_options.values())

    for i, (key, value) in enumerate(menu_options.items(), start=1):
        option_name = value.__name__.replace('handle_', '').replace('_', ' ').title()
        print(f"[{key}] {option_name.ljust(max_option_length)}", end='\t')
        if i % 2 == 0 or i == len(menu_options):
            print()
    print("\n")


def handle_exit():
    """
    Kills the program.
    """
    printer.warning("Exiting...")
    printer.info("Thanks for using H4X-Tools! Remember to star this on GitHub! \n -Vili")
    time.sleep(1)
    print(Fore.RESET)
    exit()


def handle_ig_scrape():
    """
    Handles the IG Scrape util.

    Note, you have to log in to Instagram in order to use this util.
    """
    printer.warning("NOTE! You have to log in to Instagram everytime in order to use this util.")
    printer.warning("I suggest you to create a new account for this purpose.")
    username = str(input("Your username : "))
    password = getpass("Your password : ")
    target = str(input("Enter a target username : \t")).replace(" ", "_")
    ig_scrape.Scrape(username, password, target)
    time.sleep(1)


def handle_web_search():
    """
    Handles the Web Search util.
    """
    query = str(input("Search query : \t"))
    websearch.Search(query)


def handle_phone_lookup():
    """
    Handles the Phone number Lookup util.
    """
    no = str(input("Enter a phone-number with country code : \t"))
    phonenumber_lookup.LookUp(no)


def handle_ip_lookup():
    """
    Handles the IP/Domain Lookup util.
    """
    ip = str(input("Enter a IP address OR domain : \t"))
    ip_lookup.Lookup(ip)


def handle_username_search():
    """
    Handles the Username Search util.
    """
    username = str(input("Enter a Username : \t")).replace(" ", "_")
    search_username.Search(username)


def handle_email_search():
    """
    Handles the Email Search util.

    Windows support is not available yet.
    """
    if os.name == "nt":
        printer.warning(f"Sorry, this currently only works on Linux machines :(")
    else:
        email = str(input("Enter a email address : \t"))
        email_search.Holehe(email)


def handle_port_scanner():
    """
    Handles the Port Scanner util.
    """
    ip = str(input("Enter a IP address OR domain : \t"))
    port_range = int(input("Enter number of ports to scan : \t"))
    port_scanner.Scan(ip, port_range)


def handle_webhook_spammer():
    """
    Handles the Webhook Spammer util.
    """
    url = str(input("Enter a webhook url : \t"))
    amount = int(input("Enter a amount of messages : \t"))
    message = str(input("Enter a message : \t"))
    username = str(input("Enter a username : \t"))
    throttle = int(input("Enter time of sleep (seconds) : \t"))
    webhook_spammer.Spam(url, amount, message, username, throttle)


def handle_whois_lookup():
    """
    Handles the WhoIs Lookup util.
    """
    domain = str(input("Enter a domain : \t"))
    whois_lookup.Lookup(domain)


def handle_sms_bomber():
    """
    Handles the SMS Bomber util.

    Currently only works for US numbers.
    """
    number = input("Enter the target phone number (with country code): \t")
    count = input("Enter the number of SMS to send: \t")
    throttle = input("Enter the throttle time (in seconds): \t")
    smsbomber.SMSBomber(number, count, throttle)


def handle_fake_info_generator():
    """
    Handles the Fake Info Generator util.
    """
    fake_info_generator.Generate()


def handle_web_scrape():
    """
    Handles the Web Scrape util.
    """
    url = str(input(f"Enter a url : \t"))
    web_scrape.Scrape(url)


def handle_wifi_finder():
    """
    Handles the Wi-Fi Finder util.
    """
    printer.info(f"Scanning for nearby Wi-Fi networks...")
    wifi_finder.Scan()


def handle_wifi_password_getter():
    """
    Handles the Wi-Fi Password Getter util.
    """
    printer.info(f"Scanning for locally saved Wi-Fi passwords...")
    wifi_password_getter.Scan()


def handle_dir_buster():
    """
    Handles the Dir Buster util.
    """
    url = input(f"Enter a domain : \t")
    dirbuster.Scan(url)


def handle_local_accounts_getter():
    """
    Handles the Local Accounts Getter util.
    """
    printer.info(f"Scanning for local accounts...")
    local_accounts_getter.Scan()


def handle_caesar_cipher():
    """
    Handles the Caesar Cipher util.
    """
    message = input("Enter a text to cipher/decipher : \t")
    shift = int(input("Enter a number of shifts (0 to 25) : \t"))
    if shift < 0 or shift > 25:
        printer.error("Invalid shift number, please choose a number between 0 and 25..!")
    mode = str(input("Enter a mode (encrypt/decrypt/bruteforce) : \t"))
    caesar_cipher.CaesarCipher(message, shift, mode)


def handle_basexx():
    """
    Handles the BaseXX util.
    """
    message = input("Enter a text to encode/decode : \t")
    mode = str(input("Enter a mode (encode/decode) : \t"))
    encoding = str(input("Enter a encoding (64/32/16) : \t"))
    basexx.BaseXX(message, mode, encoding)


# Create a dictionary to map menu options to corresponding functions
menu_options = {
    "1": handle_ig_scrape,
    "2": handle_web_search,
    "3": handle_phone_lookup,
    "4": handle_ip_lookup,
    "5": handle_username_search,
    "6": handle_email_search,
    "7": handle_port_scanner,
    "8": handle_webhook_spammer,
    "9": handle_whois_lookup,
    "10": handle_sms_bomber,
    "11": handle_fake_info_generator,
    "12": handle_web_scrape,
    "13": handle_wifi_finder,
    "14": handle_wifi_password_getter,
    "15": handle_dir_buster,
    "16": handle_local_accounts_getter,
    "17": handle_caesar_cipher,
    "18": handle_basexx,
    "19": about,
    "20": donate,
    "21": handle_exit
}


def main():
    """
    Main function.
    """
    internet_check()
    time.sleep(1)
    version_from_url = version_check()
    if version_from_url is None:
        printer.warning("Failed to check the version..!")
        time.sleep(1)
    elif version.strip() != version_from_url.strip():
        printer.warning(f"You are using an outdated version! ({version})")
        printer.warning("Check for updates..! (https://github.com/v1li/h4x-tools)")
        time.sleep(1)

    if os.name == "nt":
        printer.warning("Windows system detected..! Expect issues...")
        time.sleep(1)

    while True:
        print_banner()
        time.sleep(1)
        print_menu()
        a = input("[$] Select your option ~> \t")

        if a in menu_options:
            menu_options[a]()  # Call the corresponding function based on the selected option
            time.sleep(3)  # Sleep so user has time to see results.
        else:
            printer.error("Invalid option!")
            time.sleep(2)


if __name__ == "__main__":
    main()
