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

import requests
from colorama import Style

from helper import printer, randomuser, timer


@timer.timer(require_input=True)
def lookup(target: str) -> None:
    """
    Uses Hudson Rock API to gather information about an email OR domain.

    :param target: email or a domain
    """
    try:
        if "@" in target:
            url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={target}"
            target_type = "email"
        else:
            url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain={target}"
            target_type = "domain"

        headers = {"User-Agent": str(randomuser.GetUser())}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        printer.info(
            f"Looking up {target_type} {Style.BRIGHT}{target}{Style.RESET_ALL}..."
        )

        printer.noprefix("")
        printer.section("Leak Search Results")

        for key, value in data.items():
            if key == "data":
                continue

            label = key.replace("_", " ").title()

            if isinstance(value, dict):
                printer.success(f"{label} :")
                for k, v in value.items():
                    sub_label = k.replace("_", " ").title()
                    printer.success(f"    {sub_label} : {v}")
            elif isinstance(value, list):
                printer.success(f"{label} : {len(value)} item(s)")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            sub_label = k.replace("_", " ").title()
                            printer.success(f"    {sub_label} : {v}")
                        printer.noprefix("")
                    else:
                        printer.success(f"    {item}")
            else:
                printer.success(f"{label} : {value}")

        printer.noprefix("")
        printer.info(f"Raw data : {Style.BRIGHT}{url}{Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        printer.error(f"Error or the target wasn't found : {e}")
