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
from colorama import Fore
import time


class Scan:
    def __init__(self):
        if os.name == "nt":
            print(f"{Fore.GREEN}Windows system detected..! Doing a netsh scan...")
            time.sleep(1)
            try:
                os.system("netsh wlan show networks")
            except Exception as e:
                print(f"{Fore.RED}Error: ", e)
        else:
            print(f"{Fore.GREEN}Linux system detected..! Doing a nmcli scan...")
            time.sleep(1)
            try:
                os.system("nmcli dev wifi")
            except Exception as e:
                print(f"{Fore.RED}Error : ", e)
                
            