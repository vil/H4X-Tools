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


class Holehe:
    """
    Searches for the email address in various websites using holehe.

    Thanks to Holehe, https://github.com/megadose/holehe

    :param email: The email address to search for.
    """
    def __init__(self, email):
        print(f"{Fore.GREEN}[*] Trying to find sites where {email} is used, thanks to holehe.")
        time.sleep(1)
        try:
            os.system("holehe " + email)
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
