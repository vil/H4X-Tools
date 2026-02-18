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

import socket
import time

import requests
from colorama import Style

from helper import printer, randomuser, timer


@timer.timer(require_input=True)
def lookup(ip_address: str) -> None:
    """
    Gets information about a given ip address using https://ipinfo.io/

    :param ip_address: The IP address or hostname to look up.
    """
    try:
        ip_address = socket.gethostbyname(ip_address)
        url = f"https://ipinfo.io/{ip_address}/json"
        headers = {"User-Agent": str(randomuser.GetUser())}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        values = response.json()

        printer.info(
            f"Trying to find information for {Style.BRIGHT}{ip_address}{Style.RESET_ALL}..."
        )
        time.sleep(1)

        for key, value in values.items():
            if key == "readme":
                continue
            if not value:
                value = "Not Found"
            printer.success(f"{key.capitalize()} :", value)

        if "loc" in values:
            printer.success(
                "Openstreetmap URL :",
                f"https://www.openstreetmap.org/search?query={values['loc']}",
            )

    except requests.exceptions.RequestException as e:
        printer.error(f"Request error : {e}")
    except socket.gaierror as e:
        printer.error(f"Could not resolve host : {e}")
    except Exception as e:
        printer.error(f"Error : {e}")
