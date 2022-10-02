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

import json
from urllib.request import urlopen
from colorama import Fore


class FindIp:
    def __init__(self, ip):
        try:
            url = "https://ip-api.com/json/" + ip

            values = json.load(urlopen(url))
            print(f"{Fore.GREEN}[*] Ip Address : \t", values['query'])
            print(f"{Fore.GREEN}[*] Country : \t", values['country'])
            print(f"{Fore.GREEN}[*] City : \t", values['city'])
        except Exception as e:
            print(f"\n{Fore.RED}[*] Can't find any information for the given IP address!" + Fore.RESET)
            return
