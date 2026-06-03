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

import argparse
import socket
import time
from typing import Any

from colorama import Fore, Style

from helper import config, handles, printer

VERSION = "26.1"


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
{Style.RESET_ALL}v{VERSION} / Vili (@vil) - https://vili.dev
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
            "**Authenticated mode** (Instagram `sessionid` cookie) queries Instagram's private mobile API directly "
            "for richer data — business flags, IGTV count, WhatsApp link status, and publicly listed contact details. "
            "Session IDs can optionally be saved in `$HOME/.config/h4x-tools/config.json` so they do not need to be re-entered every run. "
            "Both tracks run Instagram's account-recovery lookup to surface obfuscated email and phone. "
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
            "Checks a username across a configurable number of websites using Maigret's "
            "maintained site database and detection engines. Configure site count, timeout, "
            "parallel connections, retries, and detailed errors before scanning. Results can "
            "optionally be exported to `scraped_data/maigret/` as TXT, CSV, or JSON. "
            "Credits: soxoj/maigret."
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
    "2": handles.handle_web_reconnaissance,
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


def _add_optional_tool_arg(
    parser: Any,
    *flags: str,
    dest: str,
    metavar: str,
    help_text: str,
) -> None:
    """
    Add a tool flag that may optionally receive a target value.

    If the user passes only the flag, the corresponding handler will prompt for
    the missing value. Example: ``--igscrape`` prompts, while
    ``--igscrape some_user`` uses ``some_user`` directly.
    """
    parser.add_argument(
        *flags,
        dest=dest,
        nargs="?",
        const=True,
        default=None,
        metavar=metavar,
        help=help_text,
    )


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the H4X-Tools command-line parser.

    :return: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="h4xtools",
        description="H4X-Tools - modular OSINT, reconnaissance, and scraping toolkit.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=f"H4X-Tools v{VERSION}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Enable verbose output. Repeat for more verbosity.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output. Implies verbose output.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Print the full tool help and exit.",
    )
    parser.add_argument(
        "--no-internet-check",
        action="store_true",
        help="Skip the startup internet connectivity check.",
    )

    tool_group = parser.add_argument_group(
        "Tool shortcuts",
        "Pass one or more tool flags to run them directly without opening the menu. "
        "Flags with optional values will prompt if the value is omitted.",
    )

    _add_optional_tool_arg(
        tool_group,
        "--igscrape",
        "--ig-scrape",
        "--instagram",
        "--ig",
        dest="ig_scrape",
        metavar="USERNAME",
        help_text="Run Instagram scrape for USERNAME.",
    )
    tool_group.add_argument(
        "--webrecon",
        "--web-recon",
        "--web-reconnaissance",
        action="store_true",
        help="Run the interactive deep web search workflow.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--phone",
        "--phone-lookup",
        dest="phone_lookup",
        metavar="NUMBER",
        help_text="Run phone lookup for NUMBER.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--ip",
        "--ip-lookup",
        dest="ip_lookup",
        metavar="IP_OR_DOMAIN",
        help_text="Run IP/domain lookup.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--username",
        "--username-search",
        dest="username_search",
        metavar="USERNAME",
        help_text="Run Maigret username search.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--email",
        "--email-search",
        dest="email_search",
        metavar="EMAIL",
        help_text="Run email search.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--leak",
        "--leak-search",
        dest="leak_search",
        metavar="TARGET",
        help_text="Run leak search for an email, domain, or username.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--port",
        "--port-scanner",
        dest="port_scanner",
        metavar="IP_OR_DOMAIN",
        help_text="Run port scanner for IP_OR_DOMAIN.",
    )
    tool_group.add_argument(
        "--port-range",
        type=int,
        default=None,
        help="Number of ports to scan when using --port/--port-scanner.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--whois",
        "--whois-lookup",
        dest="whois_lookup",
        metavar="DOMAIN",
        help_text="Run WHOIS lookup for DOMAIN.",
    )
    tool_group.add_argument(
        "--fake-info",
        "--fake-info-generator",
        action="store_true",
        help="Generate fake identity information.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--webscrape",
        "--web-scrape",
        dest="web_scrape",
        metavar="URL",
        help_text="Run web scrape for URL.",
    )
    tool_group.add_argument(
        "--wifi-finder",
        action="store_true",
        help="Scan for nearby Wi-Fi networks.",
    )
    tool_group.add_argument(
        "--wifi-vault",
        action="store_true",
        help="Dump locally saved Wi-Fi passwords.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--dirbuster",
        "--dir-buster",
        dest="dir_buster",
        metavar="DOMAIN",
        help_text="Run directory buster for DOMAIN.",
    )
    _add_optional_tool_arg(
        tool_group,
        "--bluetooth",
        "--bluetooth-scanner",
        dest="bluetooth_scanner",
        metavar="SECONDS",
        help_text="Run Bluetooth scanner for SECONDS.",
    )
    tool_group.add_argument(
        "--local-users",
        action="store_true",
        help="Enumerate local system users.",
    )

    return parser


def _value_or_prompt(value: object) -> str | None:
    """
    Convert argparse optional-argument sentinels to handler values.

    :param value: ``None``, ``True`` when flag has no value, or a string value.
    :return: ``None`` to make the handler prompt, otherwise the provided value.
    """
    return None if value is True or value is None else str(value)


def _cli_tool_selected(args: argparse.Namespace) -> bool:
    """
    Determine whether any direct-run tool flag was provided.

    :param args: Parsed CLI args.
    :return: ``True`` if at least one tool should run directly.
    """
    return any(
        [
            args.ig_scrape is not None,
            args.webrecon,
            args.phone_lookup is not None,
            args.ip_lookup is not None,
            args.username_search is not None,
            args.email_search is not None,
            args.leak_search is not None,
            args.port_scanner is not None,
            args.whois_lookup is not None,
            args.fake_info,
            args.web_scrape is not None,
            args.wifi_finder,
            args.wifi_vault,
            args.dir_buster is not None,
            args.bluetooth_scanner is not None,
            args.local_users,
        ]
    )


def _run_cli_tools(args: argparse.Namespace) -> None:
    """
    Execute tool flags directly and exit without opening the menu.

    Tools run in the fixed menu order when multiple flags are provided.

    :param args: Parsed CLI args.
    """
    cli_tasks = [
        (
            args.ig_scrape is not None,
            handles.handle_ig_scrape,
            [_value_or_prompt(args.ig_scrape)],
        ),
        (args.webrecon, handles.handle_web_reconnaissance, []),
        (
            args.phone_lookup is not None,
            handles.handle_phone_lookup,
            [_value_or_prompt(args.phone_lookup)],
        ),
        (
            args.ip_lookup is not None,
            handles.handle_ip_lookup,
            [_value_or_prompt(args.ip_lookup)],
        ),
        (
            args.username_search is not None,
            handles.handle_username_search,
            [_value_or_prompt(args.username_search)],
        ),
        (
            args.email_search is not None,
            handles.handle_email_search,
            [_value_or_prompt(args.email_search)],
        ),
        (
            args.leak_search is not None,
            handles.handle_leak_search,
            [_value_or_prompt(args.leak_search)],
        ),
        (
            args.port_scanner is not None,
            handles.handle_port_scanner,
            [_value_or_prompt(args.port_scanner), args.port_range],
        ),
        (
            args.whois_lookup is not None,
            handles.handle_whois_lookup,
            [_value_or_prompt(args.whois_lookup)],
        ),
        (args.fake_info, handles.handle_fake_info_generator, []),
        (
            args.web_scrape is not None,
            handles.handle_web_scrape,
            [_value_or_prompt(args.web_scrape)],
        ),
        (args.wifi_finder, handles.handle_wifi_finder, []),
        (args.wifi_vault, handles.handle_wifi_vault, []),
        (
            args.dir_buster is not None,
            handles.handle_dir_buster,
            [_value_or_prompt(args.dir_buster)],
        ),
        (
            args.bluetooth_scanner is not None,
            handles.handle_bluetooth_scanner,
            [_value_or_prompt(args.bluetooth_scanner)],
        ),
        (args.local_users, handles.handle_local_users, []),
    ]

    for selected, handler, handler_args in cli_tasks:
        if not selected:
            continue

        try:
            printer.verbose(
                f"Running {handler.__name__.replace('handle_', '').replace('_', ' ')}"
            )
            handler(*handler_args)
        except KeyboardInterrupt:
            printer.warning("Cancelled..!")
            break


def main(args: argparse.Namespace | None = None) -> None:
    if args is None:
        args = _build_parser().parse_args()

    printer.set_verbosity(verbose=args.verbose > 0, debug_enabled=args.debug)
    config.init_config()

    if args.list_tools:
        _display_help()
        return

    if not args.no_internet_check:
        _internet_check()
        time.sleep(0.5)

    printer.debug("DEBUG IS ON.")

    if _cli_tool_selected(args):
        printer.set_pause_after_tool(False)
        _run_cli_tools(args)
        return

    printer.set_pause_after_tool(True)

    while True:
        _print_banner()
        _print_menu()
        user_input = printer.user_input("Tool to execute : \t")

        if user_input.lower() in ["quit", "exit", "q", "kill"]:
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
        elif user_input.lower() in ["?", "help"]:
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
