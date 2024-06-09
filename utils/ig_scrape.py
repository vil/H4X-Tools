"""
 Copyright (c) 2024. Vili and contributors.

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

from ensta import Guest
from helper import printer, timer


class Scrape:
    """
    Scrapes data from an Instagram account.

    :param target: The username of the account to scrape.
    """
    @timer.timer
    def __init__(self, target):

        try:
            api = Guest()
            data = api.profile(target)
            self.print_user_info(data.raw)
        except Exception as e:
            printer.error(f"Error : {e}")
            return
        

    # Function to print user information
    def print_user_info(self, data):
        readable_data = { # Format
            'Username': data.get('username', 'N/A'),
            'Full Name': data.get('full_name', 'N/A'),
            'Biography': data.get('biography', 'N/A'),
            'Website': data.get('external_url', 'N/A'),
            'Followers': data.get('edge_followed_by', {}).get('count', 'N/A'),
            'Following': data.get('edge_follow', {}).get('count', 'N/A'),
            'Profile Picture URL': data.get('profile_pic_url', 'N/A'),
            'Is Private': data.get('is_private', 'N/A'),
            'Is Verified': data.get('is_verified', 'N/A'),
            'Total Posts': data.get('edge_owner_to_timeline_media', {}).get('count', 'N/A')
        }
        
        for key, value in readable_data.items():
            printer.success(f"{key} : {value}")