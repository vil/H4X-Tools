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

import requests
import random
from helper import printer, url_helper, timer
from utils import randomuser

PATH = "h4xtools/wordlist.txt"


class Scan:
    """
    Scans the given url for valid paths

    :param domain: url to scan
    """
    @timer.timer
    def __init__(self, domain):
        self.domain = domain
        self.url_list = []

        printer.info(f"Scanning for valid URLs for '{domain}'..!")
        printer.warning("This may take a while..!")
        self.scan_urls()
        printer.success(f"Scan Complete..! Found {len(self.url_list)} valid URL(s).")

    @staticmethod
    def get_wordlist():
        """
        Reads the wordlist from the url and returns a list of names

        :return: list of names
        """
        try:
            content = url_helper.read_content(PATH)
            return [line.strip() for line in content.splitlines() if line.strip()]
        except requests.exceptions.ConnectionError:
            printer.error("Connection Error..!")
            return None

    def scan_urls(self):
        """
        Scans the given domain name for valid paths
        """
        paths = self.get_wordlist()
        valid_url_count = 0

        try:
            for path in paths:
                url = f"https://{self.domain}/{path}"
                try:
                    headers = {"User-Agent": random.choice(randomuser.users)}
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        valid_url_count += 1
                        printer.success(f"{valid_url_count} Valid URL(s): {url}")
                        self.url_list.append(url)
                except requests.exceptions.ConnectionError:
                    printer.error("Connection Error..!")
                    continue
        except KeyboardInterrupt:
            printer.error("Cancelled..!")
