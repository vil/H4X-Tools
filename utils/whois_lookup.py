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

import whois
from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def check_whois(domain: str) -> None:
    """
    Looks up for the information of a given domain.

    :param domain: The domain name.
    """
    try:
        printer.info(
            f"Trying to find the information of {Style.BRIGHT}{domain}{Style.RESET_ALL}..."
        )
        q = whois.whois(domain)
        # `whois.whois()` may return a dict or an object with attributes
        try:
            items = q.items()
        except Exception:
            items = getattr(q, "__dict__", {}).items()

        for key, val in items:
            printer.success(key, "-", val)
    except Exception as e:
        printer.error("Error : ", e)
        printer.error(
            f"Make sure you have the {Style.BRIGHT}whois{Style.RESET_ALL} installed on your system..!"
        )
