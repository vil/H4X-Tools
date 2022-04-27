import json
from urllib.request import urlopen
from colorama import Fore

class find_ip:
    def __init__(self, ip):
        try :
            url="http://ip-api.com/json/"+ip

            values = json.load(urlopen(url))
            print(f"{Fore.GREEN}[*] Ip Address : \t", values['query'])
            print(f"{Fore.GREEN}[*] Country : \t", values['country'])
            print(f"{Fore.GREEN}[*] City : \t", values['city'])
            return None
        except Exception as e:
            print(f"\n{Fore.RED}Can't find any information for the given IP address!" + Fore.RESET)
            return(f"\n{Fore.RED}Can't find any information for the given IP address!" + Fore.RESET)