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

import whois
from colorama import Fore


class Lookup:
    def __init__(self, domain):
        try:
            domain = whois.query(domain)
            for key in domain.__dict__:
                print(f"{Fore.GREEN}[*] ", key, ":", domain.__dict__[key])
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
            return