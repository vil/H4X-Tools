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


from colorama import Fore
import time
import os


"""

Maigret collects a dossier on a person by username only, 
checking for accounts on a huge number of sites and gathering all the available information from web pages. 
No API keys required. Maigret is an easy-to-use and powerful fork of Sherlock.

Thanks soxoj, https://github.com/soxoj/maigret

"""


class Maigret:
    def __init__(self, username):
        print(f"{Fore.GREEN}[*] Trying to find sites where {username} is used, thanks to maigret.")
        time.sleep(1)
        try:
            os.system("maigret " + username)
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
