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
import json
from datetime import datetime
from typing import Any

from colorama import Style

from helper import printer, url_helper, timer
from helper import randomuser


@timer.timer(require_input=True)
def search(username: str) -> None:
    """
    Performs a search for the given username.

    :param username: The username to search for.
    """
    try:
        check_user_from_data(username)
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        pass


def check_user_from_data(username: str) -> dict[str, dict[str, str | int] | list[Any]]:
    """
    Scans for the given username across many different sites.

    :param username: The username to scan for.
    """
    printer.info(
        f"Searching for {Style.BRIGHT}{username}{Style.RESET_ALL} across {len(url_helper.read_local_content('resources/data.json')['sites'])} different websites..."
    )

    results = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(make_requests(username))

    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    user_json = {
        "search-params": {
            "username": username,
            "sites-number": len(
                url_helper.read_local_content("resources/data.json")["sites"]
            ),
            "date": now,
        },
        "sites": results,
    }

    return user_json


async def make_requests(username: str) -> None:
    """
    Makes the requests to the sites.

    :param username: The username to scan for.
    """
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=20)
    ) as session:
        tasks = []
        for u in url_helper.read_local_content("resources/data.json")["sites"]:
            task = asyncio.ensure_future(make_request(session, u, username))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def make_request(session, u, username) -> None:
    url = u["url"].format(username=username)
    json_body = None
    headers = {"User-Agent": f"{randomuser.GetUser()}"}
    if "headers" in u:
        headers.update(eval(u["headers"]))
    if "json" in u:
        json_body = u["json"].format(username=username)
        json_body = json.loads(json_body)
    try:
        async with session.request(
            u["method"], url, json=json_body, proxy=None, headers=headers, ssl=False
        ) as response:
            if eval(u["valid"]):
                printer.success(
                    f"#{u['id']} {Style.BRIGHT}{u['app']}{Style.RESET_ALL} - {url} [{response.status} {response.reason}]"
                )
    except Exception:
        pass
