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

import json
import requests
import socket
import time

from colorama import Style

from helper import printer, timer
from helper import randomuser


@timer.timer(require_input=True)
def lookup(ip_address: str) -> None:
    """
    Gets information about a given ip address using https://ipinfo.io/

    :param ip_address: The IP address to search for.
    """
    try:
        ip_address = socket.gethostbyname(ip_address)
        url = f"https://ipinfo.io/{ip_address}/json"
        headers = {"User-Agent": f"{randomuser.GetUser()}"}
        url = requests.get(url, headers=headers)
        # printer.info(url.text)
        values = json.loads(url.text)

        printer.info(
            f"Trying to find information for {Style.BRIGHT}{ip_address}{Style.RESET_ALL}..."
        )
        time.sleep(1)

        for value in values:
            # If value contains readme, skip it.
            if value == "readme":
                continue
            elif value == "" or value is None:
                value = "Not Found"

            printer.success(f"{value.capitalize()} :", values[value])

        printer.success(
            "Openstreetmap URL :",
            f"https://www.openstreetmap.org/search?query={values['loc']}",
        )

    except Exception as e:
        printer.error(f"Error : {e}")
        pass
