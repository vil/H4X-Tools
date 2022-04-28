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

class scan:
    def __init__(self, ip):
        ip_add = socket.gethostbyname(ip)
        try:
            for i in range (10,100,10):
                time.sleep(2)
                print("Loading", i, "%")
            print(f"\t{Fore.GREEN}[*] Successfully connected with the Server........!")
            for j in range (0,5):
                time.sleep(2)
                print(f"{Fore.GREEN}[*] Scanning for the IP address...")
            print (f"{Fore.GREEN}[*] IP Address Found ...!")
            time .sleep(5)
            for k in range (0,4):
                time.sleep(5)
                print(f"{Fore.GREEN}[*] Decoding")
            print(f"\t{Fore.GREEN}[*] IP ADDRESS OF THE WEBSITE : \t ", ip_add)
        except Exception as e:
            print(f"\t{Fore.RED}[*] Can't connect to the server" + Fore.RESET)    