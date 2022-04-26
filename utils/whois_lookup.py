import whois
from colorama import Fore

class lookup:
    def __init__(self, domain):
        try:
            domain = whois.query(domain)
            for key in domain.__dict__:
                print("[*] ", key, ":", domain.__dict__[key])
        except Exception as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
            return(f"{Fore.RED}[*] Error : ", e, Fore.RESET)