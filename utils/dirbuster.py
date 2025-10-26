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
import requests
from typing import Any

from colorama import Style

from helper import printer, url_helper, timer, randomuser

url_set = set()
target_domain: str | None = None


@timer.timer(require_input=True)
def bust(domain: str) -> None:
    """
    Scans the given url for valid paths

    param domain: url to scan
    """
    global target_domain
    target_domain = domain

    printer.info(
        f"Scanning for valid URLs for {Style.BRIGHT}{target_domain}{Style.RESET_ALL}..."
    )
    printer.warning("This may take a while...")

    scan_urls()

    printer.success(
        f"Scan Completed..! There were {Style.BRIGHT}{len(url_set)}{Style.RESET_ALL} valid URLs!"
    )


def get_wordlist() -> set[Any] | None:
    """
    Reads the wordlist from the url and returns a list of names

    :return: list of names
    """
    try:
        content = url_helper.read_local_content("resources/wordlist.txt")
        return {line.strip() for line in content.splitlines() if line.strip()}
    except requests.exceptions.ConnectionError:
        return None


async def fetch_url(session, path: str) -> None:
    """
    Fetches the url and checks if it is valid

    :param session: aiohttp session
    :param path: path to check
    """
    url = f"https://{target_domain}/{path}"
    headers = {"User-Agent": f"{randomuser.GetUser()}"}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            printer.success(
                f"{len(url_set) + 1} Valid URL(s) found : {Style.BRIGHT}{url}{Style.RESET_ALL}"
            )
            url_set.add(url)


async def scan_async(paths) -> None:
    """
    Scans the url asynchronously

    :param paths: list of paths to scan
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, path) for path in paths]
        await asyncio.gather(*tasks, return_exceptions=True)


def scan_urls() -> None:
    paths = get_wordlist()
    # printer.debug(target_domain)
    if paths is None:
        printer.error("Connection Error..!")
        return

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scan_async(paths))
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
