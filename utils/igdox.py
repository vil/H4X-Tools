# From 007-TheBond tool.
import requests
import json
from urllib.request import urlopen

class dox:
    def __init__(self, username):
        link = "https://www.instagram.com/"+username+"/?__a=1"
        response = urlopen(link)
        self.doxed = json.loads(response.read()) 
            

    def username(self):
        return self.doxed["graphql"]["user"]["username"]

    def user_id(self):
        return self.doxed["graphql"]["user"]["id"]
        
    def fullname(self):
        return self.doxed["graphql"]["user"]["full_name"]
        
    def followers(self):
        return self.doxed["graphql"]["user"]["edge_followed_by"]["count"]

    def following(self):
        return self.doxed["graphql"]["user"]["edge_follow"]["count"]

    def profile_pic(self):
        return self.doxed["graphql"]["user"]["profile_pic_url_hd"]

    def bio(self):
        return self.doxed["graphql"]["user"]["biography"]

    def posts(self):
        return self.doxed["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]
        
    def url(self):
        return self.doxed["graphql"]["user"]["external_url"]
        
    def business(self):
        return self.doxed["graphql"]["user"]["is_business_account"]
        
    def recently(self):
        return self.doxed["graphql"]["user"]["is_joined_recently"]

    def private(self):
        return self.doxed["graphql"]["user"]["is_private"]

    def verified(self):
        return self.doxed["graphql"]["user"]["is_verified"]

    def business_category(self):
        return self.doxed["graphql"]["user"]["business_category_name"]       