import requests
import time
from colorama import Fore

class spam:
    def __init__(self, url, amount, message):
        data = {
        "content" : message,
        "username" : "H4X-Tools",
        "avatar_url" : "https://cdn.discordapp.com/attachments/817858188753240104/821111284962689125/7ab097df97e8b8b41dd177a073867824_400x400.jpeg" }

        try:
            for i in range(1, amount + 1):
                requests.post(url, json=data)
                print(f"[*] Message Sent to {url} !")
                time.sleep(1)
            return None
        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}[*] Error : ", e, Fore.RESET)
            return(f"{Fore.RED}[*] Error : ", e, Fore.RESET)