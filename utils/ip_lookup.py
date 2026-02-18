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

# Human-readable labels for the keys returned by ipinfo.io.
# Any key not listed here falls back to key.replace("_", " ").title().
_IP_KEY_LABELS: dict[str, str] = {
    "ip": "IP Address",
    "hostname": "Hostname",
    "city": "City",
    "region": "Region",
    "country": "Country",
    "loc": "Coordinates",
    "org": "Organization",
    "postal": "Postal Code",
    "timezone": "Timezone",
}

# Pad all labels to this width so values line up neatly.
_KEY_WIDTH = max(len(v) for v in _IP_KEY_LABELS.values()) + 2  # = 14


@timer.timer(require_input=True)
def lookup(ip_address: str) -> None:
    """
    Gets information about a given IP address or hostname using ipinfo.io.

    :param ip_address: The IP address or hostname to look up.
    """
    try:
        ip_address = socket.gethostbyname(ip_address)
        url = f"https://ipinfo.io/{ip_address}/json"
        headers = {"User-Agent": str(randomuser.GetUser())}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        values = response.json()

        printer.info(f"Looking up {Style.BRIGHT}{ip_address}{Style.RESET_ALL}...")
        time.sleep(1)

        printer.noprefix("")
        printer.section("IP Lookup Results")

        for key, value in values.items():
            if key == "readme":
                continue
            label = _IP_KEY_LABELS.get(key, key.replace("_", " ").title())
            display_value = value if value else "N/A"
            printer.success(f"{label:<{_KEY_WIDTH}} : {display_value}")

        if "loc" in values:
            printer.noprefix("")
            printer.info(
                "OpenStreetMap : "
                f"https://www.openstreetmap.org/search?query={values['loc']}"
            )

    except requests.exceptions.RequestException as e:
        printer.error(f"Request error : {e}")
    except socket.gaierror as e:
        printer.error(f"Could not resolve host : {e}")
    except Exception as e:
        printer.error(f"Error : {e}")
