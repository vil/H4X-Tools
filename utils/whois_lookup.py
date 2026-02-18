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

import whoisdomain
from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def check_whois(domain: str) -> None:
    """
    Looks up WhoIs information for a given domain.

    :param domain: The domain name to look up.
    """
    try:
        q = whoisdomain.query(domain)
        printer.info(f"Looking up {Style.BRIGHT}{domain}{Style.RESET_ALL}...")
        printer.debug(q)
        printer.noprefix("")
        printer.section("WhoIs Results")

        for key, value in q.__dict__.items():
            # Skip None, empty strings, and empty lists/dicts.
            if value is None or value == "" or value == [] or value == {}:
                continue
            label = key.replace("_", " ").title()
            printer.success(f"{label} : {value}")

    except Exception as e:
        printer.error(f"Error : {e}")
        printer.error(
            f"Make sure {Style.BRIGHT}whois{Style.RESET_ALL} is installed on your system."
        )
