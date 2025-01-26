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

import whoisdomain, time
from helper import printer, timer
from colorama import Style


class Lookup:
    """
    Looks up for the information of a given domain.

    :param domain: The domain name.
    """
    @timer.timer
    def __init__(self, domain) -> None:
        try:
            q = whoisdomain.query(domain)
            printer.info(f"Trying to find the information of {Style.BRIGHT}{domain}{Style.RESET_ALL}...")
            for key in q.__dict__:
                printer.success(key, "-", q.__dict__[key])
        except Exception as e:
            printer.error("Error : ", e)
            printer.error(f"Make sure you have the {Style.BRIGHT}whois{Style.RESET_ALL} installed on your system..!")
