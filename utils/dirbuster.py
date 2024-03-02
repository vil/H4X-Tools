"""
 Copyright (c) 2024. Vili and contributors.

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

import asyncio, aiohttp, requests
from helper import printer, url_helper, timer
from utils import randomuser


class Scan:
    """
    Scans the given url for valid paths

    :param domain: url to scan
    """
    @timer.timer
    def __init__(self, domain):
        self.domain = domain
        self.url_set = set()

        printer.info(f"Scanning for valid URLs for '{domain}'..!")
        self.scan_urls()
        printer.success(f"Scan Complete..! Found {len(self.url_set)} valid URLs!")

    @staticmethod
    def get_wordlist():
        """
        Reads the wordlist from the url and returns a list of names

        :return: list of names
        """
        try:
            content = url_helper.read_local_content("resources/wordlist.txt")
            return {line.strip() for line in content.splitlines() if line.strip()}
        except requests.exceptions.ConnectionError:
            return None

    async def fetch_url(self, session, path):
        """
        Fetches the url and checks if it is valid

        :param session: aiohttp session
        :param path: path to check
        """
        url = f"https://{self.domain}/{path}"
        headers = {"User-Agent": f"{randomuser.IFeelLucky()}"}
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                printer.success(f"Found a valid URL - {url}")
                self.url_set.add(url)

    async def scan_async(self, paths):
        """
        Scans the url asynchronously

        :param paths: list of paths to scan
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, path) for path in paths]
            await asyncio.gather(*tasks)

    def scan_urls(self):
        paths = self.get_wordlist()
        if paths is None:
            printer.error("Connection Error..!")
            return

        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.scan_async(paths))
        except KeyboardInterrupt:
            printer.error("Cancelled..!")
