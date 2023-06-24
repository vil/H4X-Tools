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

from instagram_private_api import Client
from colorama import Fore


class Scrape:
    """
    Scrapes data from an instagram account.

    Requires username and password to log in to instagram.

    Thanks to Instagram Private API, https://pypi.org/project/instagram-private-api/

    :param target: The username of the account to scrape.
    """
    def __init__(self, target):
        # read username and password from .igscrape/username.txt and .igscrape/password.txt
        try:
            with open(".igscrape/username.txt", "r") as f:
                username = f.read()
            with open(".igscrape/password.txt", "r") as f:
                password = f.read()
        except Exception as e:
            print(f"{Fore.RED}[*] Username or password invalid!", e, Fore.RESET)
            return

        # login to instagram
        try:
            api = Client(username, password)
            data = api.username_info(target)
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
            return

        # print data
        print(f"{Fore.GREEN}[*] Scraping data from the account {target}", Fore.RESET)
        print(f"{Fore.GREEN}[*] Username : ", data["user"]["username"])
        print(f"{Fore.GREEN}[*] Full Name : ", data["user"]["full_name"])
        print(f"{Fore.GREEN}[*] Biography : ", data["user"]["biography"])
        print(f"{Fore.GREEN}[*] External Url : ", data["user"]["external_url"])
        print(f"{Fore.GREEN}[*] Followers : ", data["user"]["follower_count"])
        print(f"{Fore.GREEN}[*] Following : ", data["user"]["following_count"])
        print(f"{Fore.GREEN}[*] Is Private : ", data["user"]["is_private"])
        print(f"{Fore.GREEN}[*] Is Verified : ", data["user"]["is_verified"])
        print(f"{Fore.GREEN}[*] Profile Pic Url : ", data["user"]["hd_profile_pic_url_info"]["url"])
