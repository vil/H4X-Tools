import requests
from bs4 import BeautifulSoup
from colorama import Fore

class web:
    def __init__(self, query):
        url = "https://duckduckgo.com/html/?q=" + query
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.find_all("div", {"class": "result__body"})
        for result in results:
            title = result.find("a").text
            url = result.find("a").get("href")
            print(f"{Fore.GREEN}[*] Title : \t", title)
            print(f"{Fore.GREEN}[*] Url : \t", url)
            print("\n")
        if title and url == None:
            print(f"{Fore.RED}No results found!" + Fore.RESET)