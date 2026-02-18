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

from helper import printer
from utils import (
    bluetooth_scanner,
    deep_websearch,
    dirbuster,
    email_search,
    fake_info_generator,
    ig_scrape,
    ip_lookup,
    leak_search,
    local_users,
    phonenumber_lookup,
    port_scanner,
    search_username,
    web_scrape,
    whois_lookup,
    wifi_finder,
    wifi_vault,
)


def handle_bluetooth_scanner() -> None:
    """Handles the Bluetooth Scanner util."""
    scan_duration = int(printer.user_input("Enter a scan duration (seconds) : \t"))
    bluetooth_scanner.scan_nearby_bluetooth(duration=scan_duration)


def handle_ig_scrape() -> None:
    """Handles the IG Scrape util."""
    target = str(printer.user_input("Enter a target username : \t")).replace(" ", "_")
    ig_scrape.scrape(target=target)


def handle_deep_web_search() -> None:
    """Handles the Deep Web Search util."""
    deep_websearch.websearch()


def handle_phone_lookup() -> None:
    """Handles the Phone number Lookup util."""
    printer.info("Include the country code, e.g. +358501234567 or +12025550123")
    no = str(printer.user_input("Enter a phone-number with country code : \t"))
    phonenumber_lookup.lookup(phone_number=no)


def handle_ip_lookup() -> None:
    """Handles the IP/Domain Lookup util."""
    ip = str(printer.user_input("Enter a IP address OR domain : \t"))
    ip_lookup.lookup(ip_address=ip)


def handle_username_search() -> None:
    """Handles the Username Search util."""
    username = str(printer.user_input("Enter a target username : \t")).replace(" ", "_")
    search_username.search(username=username)


def handle_email_search() -> None:
    """Handles the Email Search util."""
    printer.info(
        "holehe will check the address against 100+ websites and show where it is registered."
    )
    email = str(printer.user_input("Enter an email address : \t"))
    email_search.search(email=email)


def handle_port_scanner() -> None:
    """Handles the Port Scanner util."""
    ip = str(printer.user_input("Enter a IP address OR domain : \t"))
    port_range = int(printer.user_input("Enter number of ports to scan : \t"))
    port_scanner.scan(ip=ip, port_range=port_range)


def handle_whois_lookup() -> None:
    """Handles the WhoIs Lookup util."""
    domain = str(printer.user_input("Enter a domain : \t"))
    whois_lookup.check_whois(domain=domain)


def handle_fake_info_generator() -> None:
    """Handles the Fake Info Generator util."""
    fake_info_generator.generate()


def handle_web_scrape() -> None:
    """Handles the Web Scrape util."""
    url = str(printer.user_input("Enter a URL : \t"))
    web_scrape.scrape(url=url)


def handle_wifi_finder() -> None:
    """Handles the Wi-Fi Finder util."""
    printer.info("Scanning for nearby Wi-Fi networks...")
    wifi_finder.scan_nearby_wifi()


def handle_wifi_vault() -> None:
    """Handles the Wi-Fi Password Getter util."""
    printer.info("Scanning for locally saved Wi-Fi passwords...")
    wifi_vault.get_local_passwords()


def handle_dir_buster() -> None:
    """Handles the Dir Buster util."""
    domain = printer.user_input("Enter a domain : \t")
    dirbuster.bust(domain=domain)


def handle_local_users() -> None:
    """Handles the Local User Enum."""
    printer.info("Scanning for local accounts...")
    local_users.scan_for_local_users()


def handle_leak_search() -> None:
    """Handles the Cybercrime Intelligence util."""
    target = printer.user_input("Enter a target (email/domain) : \t")
    leak_search.lookup(target=target)
