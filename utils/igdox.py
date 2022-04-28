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
import re
import json
import random
from colorama import Fore
from utils.randomuser import users

class dox:
    def __init__(self, username):
        link = f"https://www.instagram.com/{username}/?__a=1"
        session = requests.session()
        session.headers = random.choice(users)
        response = session.get(link)

        if response.status_code != 200:
            print(f"{Fore.RED}[*] IGDox : \t user not found..! {Fore.RESET}")

        final_process = re.sub(r'^jsonp\d+\(|\)\s+$', '', response.text)
        self.doxed = json.loads(final_process)


        data = {
        'Profile picture': self.doxed['graphql']['user']['profile_pic_url_hd'],
	    'Username': self.doxed['graphql']['user']['username'],
	    'User ID': self.doxed['graphql']['user']['id'],
	    'External URL': self.doxed['graphql']['user']['external_url'],
	    'Bio': self.doxed['graphql']['user']['biography'],
	    'Followers': self.doxed['graphql']['user']['edge_followed_by']['count'],
	    'Following': self.doxed['graphql']['user']['edge_follow']['count'],
 	    'Pronouns': self.doxed['graphql']['user']['pronouns'],
	    'Images': self.doxed['graphql']['user']['edge_owner_to_timeline_media']['count'],
	    'Videos': self.doxed['graphql']['user']['edge_felix_video_timeline']['count'],
	    'Reels': self.doxed['graphql']['user']['highlight_reel_count'],
	    'Is private?': self.doxed['graphql']['user']['is_private'],
	    'Is verified?': self.doxed['graphql']['user']['is_verified'],
	    'Is business account?': self.doxed['graphql']['user']['is_business_account'],
	    'Is professional account?': self.doxed['graphql']['user']['is_professional_account'],
	    'Is recently joined?': self.doxed['graphql']['user']['is_joined_recently'],
	    'Business category': self.doxed['graphql']['user']['business_category_name'],
	    'Category': self.doxed['graphql']['user']['category_enum'],
	    'Has guides?': self.doxed['graphql']['user']['has_guides'] }

        print(f"{Fore.GREEN} \n{self.doxed['graphql']['user']['full_name']} | IGDox \n")

        for key, value in data.items():
	        print(f"{Fore.GREEN}[*] {key} : \t {value}")
               
