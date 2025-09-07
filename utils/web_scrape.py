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

import aiohttp
import asyncio
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from colorama import Style

from helper import printer, timer
from helper import randomuser

scraped_links = set()


@timer.timer(require_input=True)
def scrape(url: str) -> None:
    """
    Scrapes links from the given url.

    :param url: url of the website.
    """
    base_url = urlparse(url).netloc
    printer.debug(f"Scraping {base_url}")

    try:
        response = printer.inp("Do you want to scrape the linked pages as well? (y/N) : ")
        if response.lower() == 'y' or response.lower() == "yes":
            printer.info(
                f"Trying to scrape links from {Style.BRIGHT}{url}{Style.RESET_ALL} and its linked pages as well...")
            printer.warning("This may take a while depending on the sizes of the sites.")

            asyncio.run(scrape_links(url, recursive=True))
            printer.success(f"Scraping linked pages completed..!")
        else:
            printer.info(f"Trying to scrape links from {Style.BRIGHT}{url}{Style.RESET_ALL}...")
            asyncio.run(scrape_links(url, recursive=False))
            printer.success(f"Scraping completed..!")
    except Exception as e:
        printer.error(f"Error : {e}")
    except KeyboardInterrupt:
        printer.error(f"Cancelled..!")


async def fetch(session, url: str) -> str:
    headers = {"User-Agent": f"{randomuser.GetUser()}"}
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def parse_links(content, base_url: str) -> list[tuple[str | bytes | Any, str]]:
    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all("a")
    return [(urljoin(base_url, link.get("href")), link.text) for link in links]


async def scrape_links(url: str, recursive=False) -> None:
    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, url)
        links = await parse_links(html_content, url)

        for href, text in links:
            if href not in scraped_links:
                scraped_links.add(href)
                printer.success(f"{len(scraped_links)} Link(s) found : {Style.BRIGHT}{href} - {text}{Style.RESET_ALL}")

                if recursive:
                    # await asyncio.sleep(0.5)
                    await scrape_links(href)  # recursively scrape linked pages
