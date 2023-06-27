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
from helper import printer
from getpass import getpass
import time


class Scrape:
    """
    Scrapes data from an instagram account.

    Requires username and password to log in to instagram.

    Thanks to Instagram Private API, https://pypi.org/project/instagram-private-api/

    :param target: The username of the account to scrape.
    """
    def __init__(self, target):
        username = input("Your username : ")
        password = getpass("Your password : ")

        # login to instagram
        try:
            api = Client(username, password)
            data = api.username_info(target)
        except Exception as e:
            printer.error(f"Error : {e}")
            return

        # print data
        printer.info(f"Scraping data from the account '{target}'")
        time.sleep(1)
        printer.success(f"Username : ", data["user"]["username"])
        printer.success(f"Full Name : ", data["user"]["full_name"])
        printer.success(f"Biography : ", data["user"]["biography"])
        printer.success(f"External Url : ", data["user"]["external_url"])
        printer.success(f"Followers : ", data["user"]["follower_count"])
        printer.success(f"Following : ", data["user"]["following_count"])
        printer.success(f"Is Private : ", data["user"]["is_private"])
        printer.success(f"Is Verified : ", data["user"]["is_verified"])
        printer.success(f"Profile Pic Url : ", data["user"]["hd_profile_pic_url_info"]["url"])
