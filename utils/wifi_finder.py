"""
Copyright (c) 2022 GNU GENERAL PUBLIC

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
from helper import printer
import time


class Scan:
    """
    Scans for the available Wi-Fi networks.

    Requires netsh for Windows and nmcli for Linux.
    """
    def __init__(self):
        if os.name == "nt":
            printer.info("Windows system detected..! Doing a netsh scan...")
            time.sleep(1)
            try:
                os.system("netsh wlan show networks")
            except Exception as e:
                printer.error(f"Error : ", e)
                pass
        else:
            printer.info(f"Linux system detected..! Doing a nmcli scan...")
            time.sleep(1)
            try:
                os.system("nmcli dev wifi")
            except Exception as e:
                printer.error(f"Error : ", e)
                pass
