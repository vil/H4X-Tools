"""
 Copyright (c) 2023. Vili and contributors.

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
from helper import printer, timer


class Scrape:
    """
    Scrapes data from an Instagram account.

    Requires username and password to log in to Instagram.

    Thanks to Instagram Private API, https://pypi.org/project/instagram-private-api/

    :param username: The username of the account to log in to.
    :param password: The password of the account to log in to.
    :param target: The username of the account to scrape.
    """
    @timer.timer
    def __init__(self, username, password, target):
        try:
            api = Client(username, password)
            data = api.username_info(target)
            printer.info(f"Logged in as '{username}'.")
        except Exception as e:
            printer.error(f"Error : {e}")
            return

        self.print_account_info(data)

    @staticmethod
    def safe_get(data, key, default=None):
        """Safely retrieves nested data from dictionaries."""
        keys = key.split('.')
        for k in keys:
            if k in data:
                data = data[k]
            else:
                return default
        return data

    def print_account_info(self, data):
        """Prints account information."""
        try:
            user = data.get('user', {})
            printer.info(f"Scraping data from the account '{user.get('username')}'...")

            printer.success(f"Username - {user.get('username')}")
            printer.success(f"Full Name - {user.get('full_name')}")
            printer.success(f"Id - {user.get('pk')}")
            printer.success(f"Biography - {user.get('biography')}")
            printer.success(f"External Url - {user.get('external_url')}")
            printer.success(f"Is Private? - {user.get('is_private')}")
            printer.success(f"Is Verified? - {user.get('is_verified')}")
            printer.success(f"Is Business? - {user.get('is_business')}")
            printer.success(f"Business Category - {user.get('category')}")

            if user.get('is_business'):
                printer.success(f"Can Direct Message? - {user.get('direct_messaging')}")
                printer.success(f"Email - {user.get('public_email')}")
                printer.success(f"Phone Number - {user.get('public_phone_country_code')} {user.get('public_phone_number')}")

            for link in self.safe_get(user, 'bio_links', []):
                printer.success(f"Bio Link(s) - {link.get('url')}")

            printer.success(f"Total Posts - {user.get('media_count')}")
            printer.success(f"Followers - {user.get('follower_count')}")
            printer.success(f"Following - {user.get('following_count')}")

            chain_suggestions = user.get('chaining_suggestions', [])
            for idx, chain in enumerate(chain_suggestions, 1):
                printer.success(f"{idx} Chaining Suggestion(s) - {chain.get('username')} - {chain.get('full_name')} ({chain.get('pk')})")

            printer.success(f"Media(s) - {user.get('media_count')}")
            printer.success(f"IGTV Video(s) - {user.get('total_igtv_videos')}")
            printer.success(f"Profile Pic Url - {self.safe_get(user, 'hd_profile_pic_url_info.url')}")
            printer.success(f"Profile Url - https://www.instagram.com/{user.get('username')}")
        except Exception as e:
            printer.error(f"Error: {e}")
