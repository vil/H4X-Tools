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

import os
import subprocess

from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def scan_nearby_wifi() -> None:
    """
    Performs a basic scan for nearby Wi-Fi networks.

    Requires netsh for Windows and nmcli for Linux.
    """
    match os.name:
        case "nt":
            _scan_windows()
        case "posix":
            _scan_linux()
        case _:
            printer.error("Unsupported platform..!")


def _scan_windows() -> None:
    printer.info(
        f"Windows system detected... Performing {Style.BRIGHT}netsh{Style.RESET_ALL} scan..."
    )
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "networks"])
        _parse_windows_output(output.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        printer.error(f"Error : {e.returncode} - {e.stderr}")


def _scan_linux() -> None:
    printer.info(
        f"Linux system detected... Performing {Style.BRIGHT}nmcli{Style.RESET_ALL} scan..."
    )
    try:
        # Use terse mode (-t) with explicit fields so the output is easy to split
        # reliably regardless of column widths or terminal size.
        # Fields: IN-USE, SSID, SIGNAL, SECURITY
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi"]
        )
        _parse_linux_output(output.decode("utf-8"))
    except FileNotFoundError:
        printer.error(
            f"Could not find {Style.BRIGHT}nmcli{Style.RESET_ALL}. "
            "Is NetworkManager installed on your system?"
        )
    except subprocess.CalledProcessError as e:
        printer.error(f"Error : {e.returncode} - {e.stderr}")
        printer.error(f"Is your system using {Style.BRIGHT}nmcli{Style.RESET_ALL}?")


def _parse_windows_output(output: str) -> None:
    """
    Parses the output of `netsh wlan show networks` and prints each network.

    :param output: Raw decoded output from netsh.
    """
    networks: list[dict] = []
    current: dict = {}

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID") and "BSSID" not in line:
            # Start of a new network block.
            if current:
                networks.append(current)
            parts = line.split(":", 1)
            current = {
                "ssid": parts[1].strip() if len(parts) > 1 else "",
                "signal": "",
                "encryption": "",
            }
        elif line.startswith("Signal"):
            parts = line.split(":", 1)
            current["signal"] = parts[1].strip() if len(parts) > 1 else ""
        elif line.startswith("Authentication"):
            parts = line.split(":", 1)
            current["encryption"] = parts[1].strip() if len(parts) > 1 else ""

    if current:
        networks.append(current)

    if not networks:
        printer.warning("No Wi-Fi networks found.")
        return

    printer.noprefix("")
    printer.section(f"Wi-Fi Networks ({len(networks)} found)")
    for network in networks:
        printer.success(
            f"  {network['ssid']}"
            f"  (Signal: {network['signal'] or 'N/A'},"
            f" Encryption: {network['encryption'] or 'N/A'})"
        )


def _parse_linux_output(output: str) -> None:
    """
    Parses the terse output of `nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi`
    and prints every visible network, marking the connected one with an asterisk.

    Terse format fields are separated by ':'. Literal colons inside field values
    are escaped as '\\:' by nmcli.

    :param output: Raw decoded terse nmcli output.
    """
    networks: list[dict] = []

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Split on unescaped colons only.
        # nmcli escapes literal colons inside values as '\:', so we split on ':'
        # that is NOT preceded by a backslash.
        import re

        parts = re.split(r"(?<!\\):", line)

        # Un-escape any '\:' sequences left in values.
        parts = [p.replace("\\:", ":") for p in parts]

        if len(parts) < 4:
            continue

        in_use, ssid, signal, security = (
            parts[0],
            parts[1],
            parts[2],
            ":".join(parts[3:]),
        )
        connected = in_use.strip() == "*"

        networks.append(
            {
                "ssid": ssid.strip() or "(hidden)",
                "signal": signal.strip(),
                "security": security.strip() or "None",
                "connected": connected,
            }
        )

    if not networks:
        printer.warning("No Wi-Fi networks found.")
        return

    printer.noprefix("")
    printer.section(f"Wi-Fi Networks ({len(networks)} found)")
    for network in networks:
        indicator = (
            f"{Style.BRIGHT}*{Style.RESET_ALL} " if network["connected"] else "  "
        )
        printer.success(
            f"{indicator}{network['ssid']}"
            f"  (Signal: {network['signal']},"
            f" Security: {network['security']})"
        )
