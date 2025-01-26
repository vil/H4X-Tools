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

import os, time, subprocess
from helper import printer, timer
from colorama import Style

class Scan:
    """
    Performs a basic scan for nearby Wi-Fi networks.

    Requires netsh for Windows and nmcli for Linux.
    """
    @timer.timer
    def __init__(self) -> None:
        if os.name == "nt":
            self.scan_windows()
        elif os.name == "posix":
            self.scan_linux()
        else:
            printer.error("Unsupported platform..!")

    @staticmethod
    def scan_windows() -> None:
        printer.info(f"Windows system detected... Performing {Style.BRIGHT}netsh{Style.RESET_ALL} scan...")
        try:
            output = subprocess.check_output(["netsh", "wlan", "show", "networks"])
            Scan.parse_output(output.decode("utf-8"), "windows")
        except subprocess.CalledProcessError as e:
            printer.error(f"Error : {e.returncode} - {e.stderr}")

    @staticmethod
    def scan_linux() -> None:
        printer.info(f"Linux system detected... Performing {Style.BRIGHT}nmcli{Style.RESET_ALL} scan...")
        try:
            output = subprocess.check_output(["nmcli", "dev", "wifi"])
            Scan.parse_output(output.decode("utf-8"), "linux")
        except subprocess.CalledProcessError as e:
            printer.error(f"Error : {e.returncode} - {e.stderr}")
            printer.error(f"Is your system using {Style.BRIGHT}nmcli{Style.RESET_ALL}?")

    @staticmethod
    def parse_output(output, platform) -> None:
        if platform == "windows":
            # Parse Windows output
            networks = []
            for line in output.splitlines():
                if "SSID" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        networks.append({"ssid": ssid, "signal": "", "encryption": ""})
            printer.info("Available Wi-Fi networks :")
            for network in networks:
                printer.info(f"  {network['ssid']} (Signal: {network['signal']}, Encryption: {network['encryption']})")
        elif platform == "linux":
            # Parse Linux output
            networks = []
            for line in output.splitlines():
                if "*" in line:
                    parts = line.split()
                    ssid = " ".join(parts[1:-3])  # Extract Wi-Fi name
                    signal = parts[-3]
                    encryption = parts[-2]
                    networks.append({"ssid": ssid, "signal": signal, "encryption": encryption})
            printer.info("Available Wi-Fi networks :")
            for network in networks:
                printer.info(f"  {network['ssid']} (Signal: {network['signal']}, Encryption: {network['encryption']})")


