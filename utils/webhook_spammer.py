import requests
import time
from colorama import Fore

class spam:
    def __init__(self, url, amount, message):
        data = {
        "content" : message,
        "username" : "H4X-Tools" }

        try:
            for i in range(1, amount + 1):
                requests.post(url, json=data)
                print(f"[*] Message Sent to {url} !")
                time.sleep(1)
            return None
        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
            return(f"{Fore.RED}[*] Error : ", e, Fore.RESET)