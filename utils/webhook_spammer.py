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

import requests
import time
from colorama import Fore


class Spam:
    def __init__(self, url, amount, message, username):
        data = {
            "content": message,
            "username": username,
            "avatar_url": "https://cdn.discordapp.com/attachments/817858188753240104/821111284962689125/7ab097df97e8b8b41dd177a073867824_400x400.jpeg"
        }

        try:
            print(f"{Fore.GREEN}[*] Trying to send {amount} messages to {url} !")
            for i in range(1, amount + 1):
                requests.post(url, json=data)
                print(f"{Fore.GREEN}[*] {str(i)} Message Sent to {url} !")
        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}[*] Error -", e, Fore.RESET)
            return
