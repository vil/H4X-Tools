
"""
 Copyright (c) 2023-2025. Vili and contributors.

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

import asyncio, aiohttp, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from helper import printer, timer
from helper import randomuser
from colorama import Style

class Scrape:
    """
    Scrapes links from the given url.
    
    :param url: url of the website.
    """
    def __init__(self, url) -> None:
        self.url = url
        self.base_url = urlparse(url).netloc
        self.scraped_links = set()

        try:
            response = printer.inp("Do you want to scrape the linked pages as well? (y/n) : ")
            if response.lower() == 'y' or response.lower() == "yes":
                printer.info(f"Trying to scrape links from {Style.BRIGHT}{self.url}{Style.RESET_ALL} and its linked pages as well...")
                printer.warning("This may take a while depending on the sizes of the sites.")

                asyncio.run(self.scrape_links(self.url, recursive=True))
                printer.success(f"Scraping linked pages completed..!")
            else:
                printer.info(f"Trying to scrape links from {Style.BRIGHT}{self.url}{Style.RESET_ALL}...")
                asyncio.run(self.scrape_links(self.url))
                printer.success(f"Scraping completed..!")

        except Exception as e:
            printer.error(f"Error : {e}")
        except KeyboardInterrupt:
            printer.error(f"Cancelled..!")

    async def fetch(self, session, url) -> str:
        headers = {"User-Agent": f"{randomuser.GetUser()}"}
        async with session.get(url, headers=headers) as response:
            return await response.text()

    async def parse_links(self, content, base_url) -> set:
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a")
        return [(urljoin(base_url, link.get("href")), link.text) for link in links]

    async def scrape_links(self, url, recursive=False) -> None:
        async with aiohttp.ClientSession() as session:
            html_content = await self.fetch(session, url)
            links = await self.parse_links(html_content, url)

            for href, text in links:
                if href not in self.scraped_links:
                    self.scraped_links.add(href)
                    printer.success(f"{len(self.scraped_links)} Link(s) found : {Style.BRIGHT}{href} - {text}{Style.RESET_ALL}")
                    if recursive:
                        # await asyncio.sleep(0.5)
                        await self.scrape_links(href)  # recursively scrape linked pages
