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

import time
import requests
from bs4 import BeautifulSoup
import random
from helper import printer
from utils.randomuser import users


class Scrape:
    """
    Scrapes links from a given website.

    :param url: The website url.
    """
    def __init__(self, url):
        try:
            r = requests.get(url)
            r.headers = random.choice(users)
            soup = BeautifulSoup(r.text, "html.parser")
            count = 0
            printer.info(f"Trying to scrape links from {url}.")
            time.sleep(1)
            for link in soup.find_all("a"):
                count += 1
                printer.info(f"found {count} link(s) : ", link.get("href"))
        except Exception as e:
            printer.error(f"Error : ", e)
            pass
