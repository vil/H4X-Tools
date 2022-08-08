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
import random
from colorama import Fore
from utils.randomuser import users


# TODO: Rewrite the whole thing.
def instagram(username):
    url = "http://instagram.com/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Instagram!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Instagram! \n" + Fore.RESET)


def pinterest(username):
    url = "http://pinterest.com/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Pinterest!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Pinterest! \n" + Fore.RESET)


def twitter(username):
    url = "http://twitter.com/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Twitter!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Twitter! \n" + Fore.RESET)


def youtube(username):
    url = "http://youtube.com/user/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Youtube!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Youtube! \n" + Fore.RESET)


def github(username):
    url = "http://github.com/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Github!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Github! \n" + Fore.RESET)


def stackoverflow(username):
    url = "http://stackoverflow.com/users/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Stackoverflow!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Stackoverflow! \n" + Fore.RESET)


def steam(username):
    url = "http://steamcommunity.com/id/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Steam!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Steam! \n" + Fore.RESET)


def reddit(username):
    url = "http://reddit.com/user/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Reddit!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Reddit! \n" + Fore.RESET)


def doxbin(username):
    url = "http://doxbin.com/upload/" + username.replace(" ", "")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Doxbin!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Doxbin! \n" + Fore.RESET)


def tiktok(username):
    url = "http://www.tiktok.com/@" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in TikTok!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in TikTok! \n" + Fore.RESET)


def xbox(username):
    url = "http://account.xbox.com/" + username
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Xbox!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Xbox! \n" + Fore.RESET)


def twitch(username):
    url = "http://www.twitch.tv/" + username.replace(" ", "_")
    r = requests.get(url)
    r.headers = random.choice(users)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Username found in Twitch!")
        print(url + "\n")
    else:
        print(Fore.RED + "Username not found in Twitch! \n" + Fore.RESET)
