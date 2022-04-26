#!/usr/bin/env python3

import os
import time
import sys
from colorama import Fore
import socket
from utils import search_realname, search_username, igdox, whois_lookup, webhook_spammer, ip_scanner, ip_lookup, phonenumber_lookup, websearch

if os.name == "nt":
    os.system("cls")
    os.system("title H4XTools")
if os.name == "posix":
    os.system("clear")


def install(package):
    os.system(f"{sys.executable} -m pip install {package}")

def internet_check():
    try:
        socket.create_connection(("www.google.com", 80))
        print(Fore.GREEN + "\n[*] Internet Connection is Available!")
        return None
    except OSError:
        print(Fore.RED + "\n[*] Warning! Internet Connection is Unavailable!")
        return None    

if __name__ == "__main__":
    print(Fore.CYAN + """
[+]    
|
|  ██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
|  ██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
|  ███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
|  ██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
|  ██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
|  ╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░ v0.2.3b
|
| by Vp (https://github.com/herravp)
|
| NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!
|
[+]

    """)

    internet_check()

    while(1):
        print(Fore.CYAN + "\n \n")
        print("[1] IGDox              ||   [2] WebSearch")
        print("[3] Phoneloopkup       ||   [4] Iplookup")
        print("[5] UsernameSearch     ||   [6] RealNameSearch")
        print("[7] IpScanner          ||   [8] WebhookSpammer")
        print("[9] WhoIs              ||   [10] About")
        print("[11] Update            ||   [12] Exit")
        print("\n")

        a = int(input("[*] Select your option : \t"))

        if a == 1:
            ig_username = str(input("Enter a Username : \t")).replace(" ", "_")
            igdox.dox(ig_username)
            time.sleep(1)
        if a == 2:
            query = str(input("Search query : \t"))
            websearch.web(query)
        if a == 3:
            no = str(input("Enter a phonenumber with country code : \t"))
            phonenumber_lookup.number(no)
        if a == 4:
            ip = str(input("Enter a IP address : \t"))
            ip_lookup.find_ip(ip)
    
        if a == 5:
            username = str(input("Enter a Username : \t")).replace(" ", "_")
            print("\n")
            search_username.instagram(username)
            search_username.pinterest(username)
            search_username.twitter(username)
            search_username.youtube(username)
            search_username.github(username)
            search_username.stackoverflow(username)
            search_username.steam(username)
            search_username.reddit(username)
            search_username.doxbin(username)
            search_username.tiktok(username)
            search_username.xbox(username)
            search_username.twitch(username)

        if a == 6:
            name = str(input("Enter a name : \t"))
            search_realname.facebook(name)
            search_realname.linkedin(name)
            search_realname.whitepages(name)
            search_realname.peoplefinders(name)
            search_realname.doxbin(name)

        if a == 7:
            url = str(input("Enter a url (Without http://) : \t"))
            print("\n")
            ip_scanner.scan(url)

        if a == 8:
            url = str(input("Enter a webhook url : \t"))
            amount = int(input("Enter a amount of messages : \t"))
            message = str(input("Enter a message : \t"))
            webhook_spammer.spam(url, amount, message)

        if a == 9:
            url = str(input("Enter a url (Without http://) : \t"))
            print("\n")
            whois_lookup.lookup(url)            

        if a == 10:
            print(Fore.GREEN + "H4XTools is a tool that helps you to find information about any person, ip address, phonenumbers, etc.\n")
            print("Or you can use it to do some other cool stuff :^) \n")
            print("NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")
            time.sleep(1)

        if a == 11:
            try:
                os.system("git fetch")
                os.system("git pull")
            except Exception as e:
                print("ERROR! Check your Internet Connection! And make sure to run this command in the root directory of the project!")
            time.sleep(1)

        if a == 12:
            print("Closing the application...")
            break

print(Fore.GREEN + "\n Thanks for using H4XTools! \n -Vp")
time.sleep(1)
print(Fore.RESET)             