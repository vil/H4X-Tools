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

import os, time, subprocess
from helper import printer, timer


class Scan:
    """
    Performs a basic scan for nearby Wi-Fi networks.

    Requires netsh for Windows and nmcli for Linux.
    """
    @timer.timer
    def __init__(self):
        if os.name == "nt":
            self.scan_windows()
        else:
            self.scan_linux()

    @staticmethod
    def scan_windows():
        printer.info("Windows system detected... Performing netsh scan...")
        time.sleep(1)
        try:
            subprocess.run(["netsh", "wlan", "show", "networks"], check=True)
        except subprocess.CalledProcessError as e:
            printer.error(f"Error: {e.returncode}")

    @staticmethod
    def scan_linux():
        printer.info("Linux system detected... Performing nmcli scan...")
        time.sleep(1)
        try:
            subprocess.run(["nmcli", "dev", "wifi"], check=True)
        except subprocess.CalledProcessError as e:
            printer.error(f"Error: {e.returncode}")

