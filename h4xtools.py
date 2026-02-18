#!/usr/bin/env python3

"""
Copyright (c) 2023-2026. Vili and contributors.

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

import socket
import time

from colorama import Fore, Style

from helper import handles, printer

VERSION = "0.3.5"


def _internet_check() -> None:
    """
    Check if the user is connected to the internet by
    creating a socket connection to a known host and port.
    """
    try:
        socket.setdefaulttimeout(3)
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
    except socket.error as sock_error:
        printer.warning(
            "Internet Connection is Unavailable or some other problem occurred..!\n{}".format(
                sock_error
            )
        )


def _print_banner() -> None:
    print(
        Fore.LIGHTBLACK_EX
        + f"""
 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀
{Style.RESET_ALL}v{VERSION} / Vili (@vil)
    """
    )


def _display_help() -> None:
    print(Fore.LIGHTCYAN_EX)
    print(
        "H4X-Tools v{} - A modular, terminal-based toolkit for OSINT, reconnaissance, and scraping - built in Python, runs on Linux and Windows.".format(
            VERSION
        )
    )
    print("Repository link: https://github.com/vil/h4x-tools")
    print("\nMade in Finland, with love.\n")

    print("Available Tools:")
    print("------------------")

    # Use a loop to print the tools in a nice format
    tools = {
        "Ig Scrape": (
            "Two-track Instagram OSINT scraper. **Guest mode** (no login) uses the `ensta` Guest API for public profile data and recent posts. "
            "**Authenticated mode** (Instagram `sessionid` cookie) uses [`toutatis`](https://github.com/megadose/toutatis) "
            "via Instagram's private mobile API for richer data — business flags, IGTV count, WhatsApp link status, and publicly listed contact details. "
            "Both tracks run Toutatis `advanced_lookup` to surface obfuscated email and phone from Instagram's account-recovery flow. "
            "Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**."
        ),
        "Deep Web Search": (
            "Multi-mode OSINT search powered by the ddgs library. Modes: General (free-form), "
            "Person (12 dorks), Email (8 dorks), Domain (12 recon dorks), Username (12 platform "
            "dorks), Phone Number (8 dorks), or Custom Dork (write your own template). "
            "Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**."
        ),
        "Phone Lookup": (
            "Validates and analyses a phone number — E.164/national/international formats, country, "
            "region, carrier, line type, and time zones via the phonenumbers library. Then runs "
            "ignorant to check social-media platform registrations."
        ),
        "IP Lookup": (
            "Resolves a hostname or IP and queries ipinfo.io for geolocation data — city, region, "
            "country, coordinates, ISP/organization, postal code, and timezone — with a direct "
            "OpenStreetMap link."
        ),
        "Username Search": (
            "Asynchronously checks a username across hundreds of websites using a bundled site "
            "database. All matches with direct profile URLs are printed in real time."
        ),
        "Email Search": (
            "Checks an email address against 100+ websites and services using holehe to identify "
            "where the address is registered. Credits: megadose/holehe."
        ),
        "Leak Search": (
            "Multi-source breach and credential intelligence for an **email address**, **domain**, or **username**. "
            "Queries [Hudson Rock Cavalier](https://cavalier.hudsonrock.com) for stealer-log records "
            "(date of compromise, stealer family, infected machine details, masked credential samples, corporate/user service counts) and, for email targets, "
            "cross-references the [ProxyNova COMB](https://api.proxynova.com/comb) dataset (3.2B+ leaked credential lines) for a total hit count. "
            "Configurable inline entry limit; results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**."
        ),
        "Port Scanner": (
            "Concurrently scans a user-defined TCP port range (1–N) on any IP or hostname using a "
            "50-thread pool. Open ports are reported in real time."
        ),
        "WhoIs Lookup": (
            "Performs a WHOIS query on a domain and displays registrar, registration/expiry dates, "
            "name servers, status flags, and registrant details."
        ),
        "Fake Info Generator": (
            "Generates a complete fake identity using Faker — name, job, company, email, phone, "
            "address, credit card details (number, type, expiry, CVV), IBAN, and location."
        ),
        "Web Scrape": (
            "Asynchronously harvests all hyperlinks from a target URL. Optionally crawls every "
            "discovered page recursively. Results can be exported to scraped_data/ as TXT, CSV, or JSON."
        ),
        "Wi-Fi Finder": (
            "Scans for nearby Wi-Fi networks using netsh (Windows) or nmcli (Linux). Reports SSID, "
            "signal strength, and security type. The currently connected network is highlighted."
        ),
        "Wi-Fi Vault": (
            "Dumps saved Wi-Fi passwords stored on the local machine using netsh (Windows) or "
            "nmcli (Linux)."
        ),
        "Dir Buster": (
            "Asynchronously bruteforces directory and file paths on a target website using a "
            "built-in wordlist, printing every URL that returns HTTP 200."
        ),
        "Bluetooth Scanner": (
            "Scans for nearby Bluetooth devices via bluetoothctl (Linux) and reports device names "
            "and MAC addresses. Windows support is coming soon."
        ),
        "Local Users": (
            "Enumerates all local user accounts on the system. Linux: username, UID, GID, full "
            "name, home directory, shell, and group. Windows: username, terminal, host, session "
            "start time, PID, SID, and domain."
        ),
        "Help": "Shows this help menu.",
    }

    for tool, description in tools.items():
        print("* {} - {}".format(tool, description))

    print("\nClosing the Toolkit:")
    print("----------------------")
    print("You can close the toolkit using the following commands:")
    print("* quit")
    print("* q")
    print("* kill")
    print("* exit")

    print("\nLicense and Credits:")
    print("---------------------")
    print(
        "H4X-Tools is under the GNU General Public License v3, made by Vili (@vil).\n"
        "This toolkit is for educational and authorised security research purposes only."
    )


def _print_menu() -> None:
    max_option_length = max(
        len(value.__name__.replace("handle_", "").replace("_", " ").title())
        for value in MENU_OPTIONS.values()
    )

    for i, (key, value) in enumerate(MENU_OPTIONS.items(), start=1):
        option_name = value.__name__.replace("handle_", "").replace("_", " ").title()
        print(
            f"{Fore.LIGHTGREEN_EX}[{key.zfill(2)}]{Style.RESET_ALL} {option_name.ljust(max_option_length)}",
            end="",
        )

        if i % 2 == 0:
            print()
        else:
            print(" " * 4, end="")

    print("\n")
    print(f"Type {Style.BRIGHT}?{Style.RESET_ALL} for help.")
    print(f"Type {Style.BRIGHT}exit{Style.RESET_ALL} to close the toolkit...")


MENU_OPTIONS = {
    "1": handles.handle_ig_scrape,
    "2": handles.handle_deep_web_search,
    "3": handles.handle_phone_lookup,
    "4": handles.handle_ip_lookup,
    "5": handles.handle_username_search,
    "6": handles.handle_email_search,
    "7": handles.handle_leak_search,
    "8": handles.handle_port_scanner,
    "9": handles.handle_whois_lookup,
    "10": handles.handle_fake_info_generator,
    "11": handles.handle_web_scrape,
    "12": handles.handle_wifi_finder,
    "13": handles.handle_wifi_vault,
    "14": handles.handle_dir_buster,
    "15": handles.handle_bluetooth_scanner,
    "16": handles.handle_local_users,
}


def main() -> None:
    _internet_check()
    time.sleep(0.5)

    printer.debug("DEBUG IS ON.")

    while True:
        _print_banner()
        _print_menu()
        user_input = printer.user_input("Tool to execute : \t")

        if user_input.lower() in {"quit", "exit", "q", "kill"}:
            # Kill the program.
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            time.sleep(0.5)
            break

        if user_input in MENU_OPTIONS:
            try:
                MENU_OPTIONS[
                    user_input
                ]()  # Call the corresponding function based on the selected option
            except KeyboardInterrupt:
                printer.warning("Cancelled..!")
        elif user_input.lower() == "?":
            _display_help()
            printer.user_input("Done reading? Press the Enter key.")
        else:
            printer.error("Invalid option!")
            time.sleep(0.5)


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except ValueError:
            printer.error("Invalid value inputted..!")
        except KeyboardInterrupt:
            print("\n")
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            exit(0)
