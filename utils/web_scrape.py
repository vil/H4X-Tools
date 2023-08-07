"""
 Copyright (c) 2023. Vili and contributors.

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

import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
from helper import printer, timer
from utils.randomuser import users


class Scrape:
    """
    Scrapes links from a given website.

    :param url: The website url.
    """
    @timer.timer
    def __init__(self, url):
        try:
            printer.info(f"Trying to scrape links from '{url}'...")
            asyncio.run(self.scrape_links(url))
            printer.success(f"Scraping completed..!")
        except Exception as e:
            printer.error(f"Error: {e}")

    @staticmethod
    async def fetch(session, url):
        headers = {"User-Agent": random.choice(users)}
        async with session.get(url, headers=headers) as response:
            return await response.text()

    @staticmethod
    async def parse_links(content):
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a")
        return [(link.get("href"), link.text) for link in links]

    async def scrape_links(self, url):
        async with aiohttp.ClientSession() as session:
            html_content = await self.fetch(session, url)

            # TODO This part can be further improved by using ThreadPoolExecutor to parse links concurrently.
            links = await self.parse_links(html_content)

            count = 0
            for href, text in links:
                count += 1
                printer.success(f"found {count} link(s): {href} - {text}")
