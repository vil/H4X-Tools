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
from colorama import Fore

def linkedin(name):
    url="http://linkedin.com/in/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Name found in Linkedin!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Linkedin! \n" + Fore.RESET)

def facebook(name):
    url="http://facebook.com/"+name.replace(" ", ".")
    r = requests.get(url)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Name found in Facebook!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Facebook! \n" + Fore.RESET)

def whitepages(name):
    url="http://whitepages.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Name found in Whitepages!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Whitepages! \n" + Fore.RESET)

def peoplefinders(name):
    url="http://peoplefinders.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Name found in Peoplefinders!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Peoplefinders! \n" + Fore.RESET)

def doxbin(name):
    url="http://doxbin.com/upload/"+name.replace(" ", "")
    r = requests.get(url)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[*] Name found in Doxbin!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Doxbin! \n" + Fore.RESET)       