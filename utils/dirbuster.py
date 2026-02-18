"""
Copyright (c) 2023-2026. Vili and contributors.

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
from colorama import Style

from helper import printer, randomuser, timer, url_helper


@timer.timer(require_input=True)
def bust(domain: str) -> None:
    """
    Scans the given url for valid paths.

    :param domain: url to scan
    """
    printer.info(
        f"Scanning for valid URLs for {Style.BRIGHT}{domain}{Style.RESET_ALL}..."
    )
    printer.warning("This may take a while...")

    valid_urls = _scan_urls(domain)

    printer.success(
        f"Scan Completed..! There were {Style.BRIGHT}{len(valid_urls)}{Style.RESET_ALL} valid URLs!"
    )


def _get_wordlist() -> set[str] | None:
    """
    Reads the wordlist from the local resources and returns a set of paths.

    :return: set of path strings, or None if an error occurs.
    """
    content = url_helper.read_local_content("resources/wordlist.txt")
    if not isinstance(content, str):
        return None
    return {line.strip() for line in content.splitlines() if line.strip()}


async def _fetch_url(
    session: aiohttp.ClientSession, domain: str, path: str, url_set: set
) -> None:
    """
    Fetches a URL and records it if it returns HTTP 200.

    :param session: aiohttp session
    :param domain: target domain
    :param path: path to check
    :param url_set: set to collect valid URLs into
    """
    url = f"https://{domain}/{path}"
    headers = {"User-Agent": str(randomuser.GetUser())}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                url_set.add(url)
                printer.success(
                    f"{len(url_set)} Valid URL(s) found : {Style.BRIGHT}{url}{Style.RESET_ALL}"
                )
    except Exception:
        pass


async def _scan_async(domain: str, paths: set[str]) -> set[str]:
    """
    Scans the domain asynchronously for all paths.

    :param domain: target domain
    :param paths: set of paths to scan
    :return: set of valid URLs found
    """
    url_set: set[str] = set()
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_url(session, domain, path, url_set) for path in paths]
        await asyncio.gather(*tasks, return_exceptions=True)
    return url_set


def _scan_urls(domain: str) -> set[str]:
    """
    Loads the wordlist and runs the async scan.

    :param domain: target domain
    :return: set of valid URLs found
    """
    paths = _get_wordlist()
    printer.debug(f"Domain: {domain}, paths loaded: {len(paths) if paths else 0}")
    if paths is None:
        printer.error("Failed to load wordlist..!")
        return set()

    try:
        return asyncio.run(_scan_async(domain, paths))
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return set()
    except RuntimeError as e:
        printer.error(f"Ran into a RuntimeError: {e}")
        return set()
