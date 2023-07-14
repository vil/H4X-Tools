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
import random
from helper import printer, url_helper
from utils import randomuser

url_list = []
PATH = "h4xtools/wordlist.txt"


class Scan:
    """
    Scans the given url for valid paths

    :param domain: url to scan
    """
    def __init__(self, domain):
        self.url_list = url_list
        self.domain = domain

        printer.info(f"Scanning for valid URLs for '{domain}'..!")
        printer.warning("This may take a while..!")
        scan_urls(domain)
        printer.success(f"Scan Complete..! Found {len(url_list)} valid URL(s)..!")


def get_wordlist():
    """
    Reads the wordlist from the url and returns a list of names

    :return: list of names
    """
    names = []
    try:
        content = url_helper.read_content(PATH)
        for line in content.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                names.append(line)
        return names
    except requests.exceptions.ConnectionError:
        printer.error("Connection Error..!")
        return None


def scan_urls(domain):
    """
    Scans the given domain name for valid paths

    :param domain: domain name to scan
    """
    paths = get_wordlist()
    valid_url = 0

    try:
        for path in paths:
            url = f"https://{domain}/{path}"
            try:
                headers = {"User-Agent": random.choice(randomuser.users)}
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    valid_url += 1
                    printer.success(f"{valid_url} Valid URL(s): {url}")
                    url_list.append(url)
            except requests.exceptions.ConnectionError:
                printer.error("Connection Error..!")
                continue
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        pass

    return url_list
