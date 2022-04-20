#!/usr/bin/env python3

import requests
import os
import time
import random
import sys
import json
from bs4 import BeautifulSoup
import phonenumbers as p
from phonenumbers import geocoder
from phonenumbers import carrier
import urllib
from urllib.request import urlopen
from utils.igdox import dox
from utils.search_everywhere import *

if os.name == "nt":
    os.system("cls")
    os.system("title H4XTools")
if os.name == "posix":
    os.system("clear")


def install(package):
    os.system(f"{sys.executable} -m pip install {package}")


try:
    from colorama import Fore
except ModuleNotFoundError:
    install("colorama")

## IG Dox
def igdoxed(ig_username):
    try:
        print("\n")
        acc = dox(ig_username)
        print("[*] Username: " + ig_username)
        print("[*] Fullname: " + str(acc.fullname()))
        print("[*] Profile Picture: " + str(acc.profile_pic()))
        print("[-] Id : " + str(acc.user_id()))
        print("[*] Url : " + str(acc.url()))
        print("[*] Number of Post  : " + str(acc.posts()))
        print("[*] Followers : " + str(acc.followers()))
        print("[*] Following : " + str(acc.following()))
        print("[*] Bio : " + str(acc.bio()))    
        
        if acc.private() == False:
            print("[*] Private Account : No")
        else:
            print("[*] Private Account : Yes")
            if acc.verified() == False:
                print("[*] Verified: No")
            else:
                print("[*] Verified : Yes")
                print(acc.verified())
                
        print('\n')
        return None
    except urllib.error.HTTPError as e:
        print("User not found")
        return ("User not found")

# Search using duckduckgo
def web_search(query):
    url = "https://duckduckgo.com/html/?q=" + query
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all("div", {"class": "result__body"})
    for result in results:
        title = result.find("a").text
        url = result.find("a").get("href")
        print("[*] Title : \t", title)
        print("[*] Url : \t", url)
        print("\n")
    if title and url == None:
        print("No results found!")


# Phonenumber
def number(no):
    print("\n")
    try:
        ph_no = p .parse(no)
        geo_location = geocoder.description_for_number(ph_no,'en')
        no_carrier = carrier.name_for_number(ph_no,'en')
        print ("Country : ",geo_location)
        print ("Sim Provider : ", no_carrier)
        return None
    except Exception :
        print("No data found for this number")
        return("No data found for this number")

## Ip lookup
def find_ip(ip):
    try :
        #ip=str(input ("Enter Ip address "))
        url="http://ip-api.com/json/"+ip

        values = json.load(urlopen(url))
        print("[*] Ip Address : ",values['query'])
        print("[*] Country :\t ",values['country'])
        print("[*] City : ",values['city'])
        return None
    except Exception as e:
        print("\n Can't find any information for the given ip address ")
        return("\n Can't find any information for the given ip address ")




if __name__ == "__main__":
    print(Fore.CYAN + """
[+]    
|
|  ██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
|  ██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
|  ███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
|  ██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
|  ██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
|  ╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░ v0.2.1b
|
| by Vp (https://github.com/herravp)
|
| NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!
|
[+]

    """)

    while(1):
        print(Fore.CYAN + "\n \n")
        print("[1] IGDox             ||  [2] WebSearch")
        print("[3] Phoneloopkup      ||  [4] Iplookup")
        print("[5] SearchEverywhere  ||  [6] Update")
        print("[7] About             ||  [8] Exit")
        print("\n")
        a = int(input("Select your option :\t"))
        if a == 1:
            ig_username = str(input("Username : \t"))
            igdoxed(ig_username)
            time.sleep(1)
        if a == 2:
            query = str(input("Search query : \t"))
            web_search(query)
        if a == 3:
            no = str(input("Enter number with country code : \t"))
            number(no)
        if a == 4:
            ip = str(input("Enter Ip address : \t"))
            find_ip(ip)
    
        if a == 5:
            name = str(input("Enter Username : \t"))
            print("\n")
            instagram(name)
            facebook(name)
            pinterest(name)
            twitter(name)
            linkedin(name)
            youtube(name)
            github(name)
            stackoverflow(name)
            steam(name)
            reddit(name)

        if a == 6:
            try:
                os.system("git fetch")
                os.system("git pull")
            except Exception as e:
                print("ERROR! Check your Internet Connection or No repository found!")
            time.sleep(1)    

        if a == 7:
            print(Fore.GREEN + "H4XTools is a tool that helps you to find information about any person, ip address, phonenumbers, etc.\n")
            print("Or you can use it to do some other cool stuff :^) \n")
            print("NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")
            time.sleep(1)    

        if a == 8:
            print("Closing the application in 3 second")
            time.sleep(3)
            break

print(Fore.GREEN + "\n Thanks for using H4XTools! \n -Vp")
time.sleep(1)
print(Fore.WHITE)             