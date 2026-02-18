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
import json
from datetime import datetime

import aiohttp
from colorama import Style

from helper import printer, randomuser, timer, url_helper


@timer.timer(require_input=True)
def search(username: str) -> None:
    """
    Performs a search for the given username.

    :param username: The username to search for.
    """
    try:
        _check_user_from_data(username)
    except KeyboardInterrupt:
        printer.error("Cancelled..!")


def _check_user_from_data(username: str) -> dict:
    """
    Scans for the given username across many different sites.

    :param username: The username to scan for.
    :return: A dict summarising the search parameters and matched sites.
    """
    # Read the data file once and reuse it throughout this call.
    data = url_helper.read_local_content("resources/data.json")
    if not isinstance(data, dict):
        printer.error("Failed to load site data.")
        return {}

    sites = data.get("sites", [])
    printer.info(
        f"Searching for {Style.BRIGHT}{username}{Style.RESET_ALL} "
        f"across {len(sites)} different websites..."
    )

    printer.noprefix("")
    printer.section("Username Search Results")

    results = asyncio.run(_make_requests(username, sites))

    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    user_json = {
        "search-params": {
            "username": username,
            "sites-number": len(sites),
            "date": now,
        },
        "sites": results,
    }

    return user_json


async def _make_requests(username: str, sites: list) -> list:
    """
    Makes the requests to all sites and returns a list of matched results.

    :param username: The username to scan for.
    :param sites: List of site configuration dicts from data.json.
    :return: List of site dicts where the username was found.
    """
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=20)
    ) as session:
        tasks = [
            asyncio.ensure_future(_make_request(session, content, username))
            for content in sites
        ]
        results = await asyncio.gather(*tasks)

    # Filter out None entries (sites where the username was not found).
    return [r for r in results if r is not None]


async def _make_request(
    session: aiohttp.ClientSession, content: dict, username: str
) -> dict | None:
    """
    Makes a single request to one site and returns the site dict on a match.

    :param session: The shared aiohttp client session.
    :param content: Site configuration dict from data.json.
    :param username: The username to check.
    :return: The site dict if the username was found, otherwise None.
    """
    url = content["url"].format(username=username)
    json_body = None
    headers = {"User-Agent": str(randomuser.GetUser())}

    if "headers" in content:
        # NOTE: eval() is used here because the data.json format stores headers
        # as Python expression strings. Treat data.json as trusted input only.
        headers.update(eval(content["headers"]))  # noqa: S307

    if "json" in content:
        json_body = json.loads(content["json"].format(username=username))

    try:
        async with session.request(
            content["method"],
            url,
            json=json_body,
            proxy=None,
            headers=headers,
            ssl=False,
        ) as response:
            # `valid` is a Python expression string evaluated against the response.
            # NOTE: same caveat as above — data.json must be trusted.
            if eval(content["valid"]):  # noqa: S307
                printer.success(
                    f"{Style.BRIGHT}{content['app']:<20}{Style.RESET_ALL} : {url}"
                )
                return content
    except Exception:
        pass

    return None
