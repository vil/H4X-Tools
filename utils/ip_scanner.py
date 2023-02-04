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

import socket
import time
from colorama import Fore


class Scan:
    def __init__(self, ip):
        try:
            ip_addr = socket.gethostbyname(ip)
            print(Fore.GREEN + f"[*] Trying to find the IP address of {ip}")
            time.sleep(1)
            print(f"{Fore.GREEN}[*] IP address of the website : \t ", ip_addr)
        except Exception as e:
            print(f"{Fore.RED}[*] Can't connect to the server..!" + Fore.RESET)
            print(f"{Fore.RED}[*] Detailed error : ", e)
