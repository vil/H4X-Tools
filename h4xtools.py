import requests
import os
import time
import random
import sys
from utils.igdox import dox
from urllib.request import urlopen
import urllib

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
def igdoxed(inputt):
    try:
        print("\n")
        acc = dox(inputt)
        print("[*] Username: " + inputt)
        
        print("[-] Id : " + str(acc.user_id()))
        
        print("[*] Url : " + str(acc.url()))
        print("[*] Number of Post  : " + str(acc.posts()))
        
        print("[*] Followers : " + str(acc.followers()))
        
        print("[*] Number of following :\t    " + str(acc.following()))
    
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

if __name__ == "__main__":
    print(Fore.CYAN + """
[+]    
|
|  ██╗░░██╗░░██╗██╗██╗░░██╗████████╗░█████╗░░█████╗░██╗░░░░░░██████╗
|  ██║░░██║░██╔╝██║╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
|  ███████║██╔╝░██║░╚███╔╝░░░░██║░░░██║░░██║██║░░██║██║░░░░░╚█████╗░
|  ██╔══██║███████║░██╔██╗░░░░██║░░░██║░░██║██║░░██║██║░░░░░░╚═══██╗
|  ██║░░██║╚════██║██╔╝╚██╗░░░██║░░░╚█████╔╝╚█████╔╝███████╗██████╔╝
|  ╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝╚═════╝░ v0.1
|
| by Vp (https://github.com/herravp)
|
| NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!
|
[+]

    """)

    while(1):
        print(Fore.BLUE + "\n \n")
        print("[1] InstagramDox || [2] Search")
        print("[3] Phoneloopkup || [4] Iplookup")
        print("[5] Update       || [6] Search username Across the Social Media")
        print("[7] About        || [8] Exit")
        print("\n")
        a = int(input("Select your option :\t"))
        if a == 1:
            inputt = str(input("Username : "))
            igdoxed(inputt)
        if a == 2:
            query = str(input("Search :"))
            web_search(query)
        if a == 3:
            no = str(input("Enter number with country code : \t"))
            number(no)
        if a == 4:
            ip = str(input("Enter Ip address : \t"))
            find_ip(ip)
        if a == 5:
            try:
                os.system("git pull")
            except Exception as e:
                print("ERROR! Check your Internet Connection or No repository found!")
        if a == 6:
            name = str(input("Enter Username"))
            instagram(name)
            facebook(name)
            pinrest(name)

        if a == 7:
            print(Fore.GREEN + "H4XTools is a tool that helps you to find information about any person using their socials.\n")
            print("Or you can use it to do some other cool stuff :^) \n")
            print("NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")    

        if a == 8:
            print("Closing the application in 3 second")
            time.sleep(3)
            break
        else:
            print("Invalid option.")
            time.sleep(1)