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
from helper import printer, timer
import time
import subprocess


class Scan:
    """
    Scans for the available Wi-Fi networks.

    Requires netsh for Windows and nmcli for Linux.
    """
    @timer.timer
    def __init__(self):
        if os.name == "nt":
            printer.info("Windows system detected..! Doing a netsh scan...")
            time.sleep(1)
            try:
                subprocess.run(["netsh", "wlan", "show", "networks"], check=True)
            except subprocess.CalledProcessError as e:
                printer.error(f"Error : {e.returncode}")
        else:
            printer.info("Linux system detected..! Doing a nmcli scan...")
            time.sleep(1)
            try:
                subprocess.run(["nmcli", "dev", "wifi"], check=True)
            except subprocess.CalledProcessError as e:
                printer.error(f"Error : {e.returncode}")
