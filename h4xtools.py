#!/usr/bin/env python3

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

import os
import time
from colorama import Fore
import socket
import requests
from utils import email_search, search_username, ig_scrape, whois_lookup, webhook_spammer, ip_scanner, ip_lookup, \
    phonenumber_lookup, websearch, smsbomber, tokenlogger_generator, twitter_scraping, web_scrape

if os.name == "nt":
    os.system("cls")
    os.system("title H4X-Tools")
if os.name == "posix":
    os.system("clear")


def internet_check():
    try:
        socket.create_connection(("www.google.com", 80))
        print(Fore.GREEN + "\n[*] Internet Connection is Available!")
        return None
    except OSError:
        print(Fore.RED + "\n[*] Warning! Internet Connection is Unavailable!")
        return None


def version_check():
    url = "https://raw.githubusercontent.com/V1li/H4X-Tools-ver/master/version.txt"
    # Get the version from the url and return it
    try:
        r = requests.get(url)
        return r.text
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "[*] Error! Couldn't connect to the server!")
        return None


def main():
    version = "0.2.8"
    version_from_url = version_check()

    # Check if the user is using the latest version
    if version.strip() != version_from_url.strip():
        print(Fore.RED + f"[*] Version mismatch! ({version}) ... Should be ({version_from_url})")
        time.sleep(3)
    else:
        print(Fore.GREEN + f"[*] Version matches! ({version})")
        time.sleep(1)

    print(Fore.CYAN + f"""
[+]    
|
|  ██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
|  ██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
|  ███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
|  ██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
|  ██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
|  ╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░ v{version}
|
| by Vili (https://vili.dev)
|
| NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!
|
[+]

    """)

    internet_check()

    while 1:
        print(Fore.CYAN)
        print("[1] IG Scrape          ||   [2] Web Search")
        print("[3] Phone Lookup       ||   [4] Ip Lookup")
        print("[5] Username Search    ||   [6] Email Search")
        print("[7] Ip Scanner         ||   [8] Webhook Spammer")
        print("[9] WhoIs              ||   [10] SMS Bomber (US Only!)")
        print("[11] TLogger Generator ||   [12] Twitter Scrape")
        print("[13] Web Scrape        ||   [14] About")
        print("[15] Update            ||   [16] Exit")
        print("\n")

        a = input("[*] Select your option : \t")

        if a == "1":
            if not os.path.exists("igscrape"):
                os.mkdir("igscrape")
                print(Fore.RED + "[*] It appears that you are running this tool for the first time!")
                print(
                    Fore.RED + "[*] Put your credentials in the file named 'username.txt' and 'password.txt' in the 'igscrape' folder!")
                b = input(Fore.RED + "[*] Or do you want to type your credentials now? (y/n) : ")
                if b == "y":
                    c = input("[*] Enter your username : \t")
                    d = input("[*] Enter your password : \t")
                    with open("igscrape/username.txt", "w") as f:
                        f.write(c)
                    with open("igscrape/password.txt", "w") as f:
                        f.write(d)
                    print(Fore.GREEN + "[*] Credentials saved!")
                    time.sleep(2)
                print(Fore.GREEN + "[*] Done! Now you can run the tool again!")

            else:
                # If username.txt or password.txt is empty then ask for credentials
                if os.stat("igscrape/username.txt").st_size == 0 or os.stat("igscrape/password.txt").st_size == 0:
                    print(Fore.RED + "[*] username.txt/password.txt is empty!")
                    return
                target = str(input("Enter a Username : \t")).replace(" ", "_")
                ig_scrape.Scrape(target)
                time.sleep(1)

        elif a == "2":
            query = str(input("Search query : \t"))
            websearch.Search(query)

        elif a == "3":
            no = str(input("Enter a phone-number with country code : \t"))
            phonenumber_lookup.LookUp(no)

        elif a == "4":
            ip = str(input("Enter a IP address / url (without http://) : \t"))
            ip_lookup.Lookup(ip)

        elif a == "5":
            username = str(input(f"{Fore.GREEN}Enter a Username : \t")).replace(" ", "_")
            search_username.Sherlock(username)

        elif a == "6":
            email = str(input(f"{Fore.GREEN}Enter a email address : \t"))
            email_search.Holehe(email)

        elif a == "7":
            url = str(input("Enter a url (Without http://) : \t"))
            ip_scanner.Scan(url)

        elif a == "8":
            url = str(input("Enter a webhook url : \t"))
            amount = int(input("Enter a amount of messages : \t"))
            message = str(input("Enter a message : \t"))
            username = str(input("Enter a username : \t"))
            webhook_spammer.Spam(url, amount, message, username)

        elif a == "9":
            url = str(input("Enter a url (Without http://) : \t"))
            whois_lookup.Lookup(url)

        elif a == "10":
            number = str(input("Enter mobile number : \t")).strip("+")
            count = int(input("Enter number of Messages : \t"))
            throttle = int(input("Enter time of sleep : \t"))
            smsbomber.Spam(number, count, throttle)

        elif a == "11":
            print(f"{Fore.RED}Note! Tokenlogger only works on Windows machines!")
            webhook_url = input(f"{Fore.GREEN}Enter a webhook url : \t")
            tokenlogger_generator.Create(webhook_url)

        elif a == "12":
            twitter_scraping.scraping_options()

        elif a == "13":
            url = str(input(f"{Fore.GREEN}Enter a url : \t"))
            web_scrape.Scrape(url)

        elif a == "14":
            print(
                f"{Fore.GREEN}H4X-Tools is a tool that helps you to find information about any person, ip address, phonenumbers, etc.\n")
            print("Or you can use it to do some other cool stuff :^) \n")
            print("NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")
            time.sleep(1)

        elif a == "15":
            try:
                os.system("git fetch")
                os.system("git pull")
                print(Fore.GREEN + "[*] Updated H4X-Tools. Checking for sherlock now...")
                if os.path.exists("sherlock"):
                    os.system("cd sherlock && git fetch && git pull")
                    print(Fore.GREEN + "[*] Updated sherlock!")
                else:
                    print(Fore.RED + "[*] sherlock not found..! Have you used username search before?")
            except Exception as e:
                print(Fore.RED + f"[*] Error! {e}")
            time.sleep(1)

        elif a == "16":
            print(Fore.RED + "Exiting...")
            print(Fore.GREEN + "Thanks for using H4X-Tools! Remember to star this on GitHub! \n -Vili")
            time.sleep(1)
            print(Fore.RESET)
            break

        else:
            print(Fore.RED + "Invalid option!")
            time.sleep(1)


if __name__ == '__main__':
    main()
