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
import sys


"""

Maigret collects a dossier on a person by username only, 
checking for accounts on a huge number of sites and gathering all the available information from web pages. 
No API keys required. Maigret is an easy-to-use and powerful fork of Sherlock.

Thanks soxoj, https://github.com/soxoj/maigret

"""


def install(package):
    if os.name == "nt":
        os.system(f"{sys.executable} -m pip install {package}")
    else:
        os.system(f"sudo {sys.executable} -m pip install {package}")


class Maigret:
    def __init__(self, username):
        try:
            import maigret
        except ModuleNotFoundError:
            print(f"{Fore.RED}[*] Installing maigret for you... Might ask for sudo password.")
            install("maigret")
            print(f"{Fore.GREEN}[*] Installed maigret successfully! You may rerun it now.")
            return

        print(f"{Fore.GREEN}[*] Trying to find sites where {username} is used, thanks to maigret.")
        time.sleep(1)
        try:
            os.system("maigret " + username)
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
