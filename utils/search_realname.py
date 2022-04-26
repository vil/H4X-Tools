import requests
from colorama import Fore

def linkedin(name):
    url="http://linkedin.com/in/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Linkedin!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Linkedin \n" + Fore.RESET)

def facebook(name):
    url="http://facebook.com/"+name.replace(" ", ".")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Facebook!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Facebook \n" + Fore.RESET)

def whitepages(name):
    url="http://whitepages.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Whitepages!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Whitepages \n" + Fore.RESET)

def peoplefinders(name):
    url="http://peoplefinders.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Peoplefinders!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Peoplefinders \n" + Fore.RESET)

def doxbin(name):
    url="http://doxbin.com/upload/"+name.replace(" ", "")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Doxbin!")
        print(url + "\n")
    else:
        print(Fore.RED + "Name not found in Doxbin \n" + Fore.RESET)       