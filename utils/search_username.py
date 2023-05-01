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
import os
import sys

"""

Searches websites for the given username using sherlock.

Thanks to sherlock team, https://github.com/sherlock-project/sherlock

"""


class Sherlock:
    def __init__(self, username):
        if not os.path.exists("sherlock"):
            print(f"{Fore.RED}[*] Installing sherlock for you...")
            try:
                os.system("git clone https://github.com/sherlock-project/sherlock.git")
                print(f"{Fore.GREEN}[*] Cloned sherlock successfully. Now installing requirements.", Fore.RED)
                os.system(f"cd sherlock && {sys.executable} -m pip install -r requirements.txt")
                print(f"{Fore.GREEN}[*] Installed requirements successfully.")
            except Exception as e:
                print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
        try:
            os.system(f"cd sherlock && {sys.executable} sherlock/sherlock.py --nsfw {username}")
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
