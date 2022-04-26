import requests
import re
import json
from colorama import Fore

class dox:
    def __init__(self, username):
        link = f"https://www.instagram.com/{username}/channel/?__a=1"
        session = requests.session()
        session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'}
        response = session.get(link)

        if response.status_code != 200:
            print(f"{Fore.RED} [*] IGDox : \t user not found..! {Fore.RESET}")

        final_process = re.sub(r'^jsonp\d+\(|\)\s+$', '', response.text)
        self.doxed = json.loads(final_process)


        data = {
        '[*] Profile picture': self.doxed['graphql']['user']['profile_pic_url_hd'],
	    '[*] Username': self.doxed['graphql']['user']['username'],
	    '[*] User ID': self.doxed['graphql']['user']['id'],
	    '[*] External URL': self.doxed['graphql']['user']['external_url'],
	    '[*] Bio': self.doxed['graphql']['user']['biography'],
	    '[*] Followers': self.doxed['graphql']['user']['edge_followed_by']['count'],
	    '[*] Following': self.doxed['graphql']['user']['edge_follow']['count'],
 	    '[*] Pronouns': self.doxed['graphql']['user']['pronouns'],
	    '[*] Images': self.doxed['graphql']['user']['edge_owner_to_timeline_media']['count'],
	    '[*] Videos': self.doxed['graphql']['user']['edge_felix_video_timeline']['count'],
	    '[*] Reels': self.doxed['graphql']['user']['highlight_reel_count'],
	    '[*] Is private?': self.doxed['graphql']['user']['is_private'],
	    '[*] Is verified?': self.doxed['graphql']['user']['is_verified'],
	    '[*] Is business account?': self.doxed['graphql']['user']['is_business_account'],
	    '[*] Is professional account?': self.doxed['graphql']['user']['is_professional_account'],
	    '[*] Is recently joined?': self.doxed['graphql']['user']['is_joined_recently'],
	    '[*] Business category': self.doxed['graphql']['user']['business_category_name'],
	    '[*] Category': self.doxed['graphql']['user']['category_enum'],
	    '[*] Has guides?': self.doxed['graphql']['user']['has_guides'] }

        print(f"{Fore.GREEN} \n{self.doxed['graphql']['user']['full_name']} | IGDox")

        for key, value in data.items():
	        print(f"{Fore.CYAN} [*] {key} : \t {value}")
               
