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
from helper import printer
import time, os, json, base64
from colorama import Fore
from getpass import getpass


def handle_exit() -> None:
    """
    Kills the program.
    """
    printer.warning("Exiting...")
    printer.info("Thanks for using H4X-Tools! Remember to star this on GitHub!\n -Vili")
    time.sleep(0.5)
    print(Fore.RESET)
    

def handle_ig_scrape() -> None:
    """
    Handles the IG Scrape util.

    Note, you have to log in to Instagram in order to use this util.
    """
    target = str(input("Enter a target username : \t")).replace(" ", "_")
    ig_scrape.Scrape(target)
    time.sleep(1)


def handle_web_search() -> None:
    """
    Handles the Web Search util.
    """
    printer.info("For advanced searching, you can use DuckDuckGo's advanced syntaxing. Please refer to this guide: \nhttps://duckduckgo.com/duckduckgo-help-pages/results/syntax/")
    query = str(input("Search query : \t"))
    websearch.Search(query)


def handle_phone_lookup() -> None:
    """
    Handles the Phone number Lookup util.
    """
    no = str(input("Enter a phone-number with country code : \t"))
    phonenumber_lookup.LookUp(no)


def handle_ip_lookup() -> None:
    """
    Handles the IP/Domain Lookup util.
    """
    ip = str(input("Enter a IP address OR domain : \t"))
    ip_lookup.Lookup(ip)


def handle_username_search() -> None:
    """
    Handles the Username Search util.
    """
    username = str(input("Enter a Username : \t")).replace(" ", "_")
    search_username.Search(username)


def handle_email_search() -> None:
    """
    Handles the Email Search util.

    Windows support is not available yet.
    """
    if os.name == "nt":
        printer.warning(f"Sorry, this currently only works on Linux machines :(")
    else:
        email = str(input("Enter a email address : \t"))
        email_search.Holehe(email)


def handle_port_scanner() -> None:
    """
    Handles the Port Scanner util.
    """
    ip = str(input("Enter a IP address OR domain : \t"))
    port_range = int(input("Enter number of ports to scan : \t"))
    port_scanner.Scan(ip, port_range)


def handle_webhook_spammer() -> None:
    """
    Handles the Webhook Spammer util.
    """
    url = str(input("Enter a webhook url : \t"))
    amount = int(input("Enter a amount of messages : \t"))
    message = str(input("Enter a message : \t"))
    username = str(input("Enter a username : \t"))
    throttle = int(input("Enter time of sleep (seconds) : \t"))
    webhook_spammer.Spam(url, amount, message, username, throttle)


def handle_whois_lookup() -> None:
    """
    Handles the WhoIs Lookup util.
    """
    domain = str(input("Enter a domain : \t"))
    whois_lookup.Lookup(domain)


def handle_sms_bomber() -> None:
    """
    Handles the SMS Bomber util.

    Currently only works for US numbers.
    """
    number = input("Enter the target phone number (with country code): \t")
    count = input("Enter the number of SMS to send: \t")
    throttle = input("Enter the throttle time (in seconds): \t")
    smsbomber.SMSBomber(number, count, throttle)


def handle_fake_info_generator() -> None:
    """
    Handles the Fake Info Generator util.
    """
    fake_info_generator.Generate()


def handle_web_scrape() -> None:
    """
    Handles the Web Scrape util.
    """
    url = str(input(f"Enter a url : \t"))
    web_scrape.Scrape(url)


def handle_wifi_finder() -> None:
    """
    Handles the Wi-Fi Finder util.
    """
    printer.info(f"Scanning for nearby Wi-Fi networks...")
    wifi_finder.Scan()


def handle_wifi_password_getter() -> None:
    """
    Handles the Wi-Fi Password Getter util.
    """
    printer.info(f"Scanning for locally saved Wi-Fi passwords...")
    wifi_password_getter.Scan()


def handle_dir_buster() -> None:
    """
    Handles the Dir Buster util.
    """
    url = input(f"Enter a domain : \t")
    dirbuster.Scan(url)


def handle_local_accounts_getter() -> None:
    """
    Handles the Local Accounts Getter util.
    """
    printer.info(f"Scanning for local accounts...")
    local_accounts_getter.Scan()


def handle_caesar_cipher() -> None:
    """
    Handles the Caesar Cipher util.
    """
    message = input("Enter a text to cipher/decipher : \t")
    mode = str(input("Enter a mode (encrypt/decrypt/bruteforce) : \t"))
    caesar_cipher.CaesarCipher(message, mode)


def handle_basexx() -> None:
    """
    Handles the BaseXX util.
    """
    message = input("Enter a text to encode/decode : \t")
    mode = str(input("Enter a mode (encode/decode) : \t"))
    encoding = str(input("Enter a encoding (64/32/16) : \t"))
    basexx.BaseXX(message, mode, encoding)