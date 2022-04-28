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