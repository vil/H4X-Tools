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

import time, requests
from helper import printer, timer
from helper import randomuser
from colorama import Style


class Scan:
    """
    Uses Hudson Rock API to gather information about a email OR domain.
    
    :param target: email or a domain
    """
    @timer.timer
    def __init__(self, target) -> None:
        try:
            if '@' in target:
                url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={target}"
                target_type = 'email'
            else:
                url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain={target}"
                target_type = 'domain'

            headers = {'User-Agent': f"{randomuser.GetUser()}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            printer.info(f"Trying to find information for the {target_type} {Style.BRIGHT}{target}{Style.RESET_ALL}...")

            for key, value in data.items():
                if key == "data":
                    continue
                if isinstance(value, dict):
                    printer.success(f"{key.capitalize()} :")
                    for k, v in value.items():
                        printer.success(f"  /__: {k.capitalize()} : {v}")
                else:
                    printer.success(f"{key.capitalize()} : {value}")
                
            printer.info(f"View the raw data here : {Style.BRIGHT}{url}{Style.RESET_ALL}")

        except requests.exceptions.RequestException as e:
            printer.error(f"Error or the target wasn't found : {e}")
            pass
