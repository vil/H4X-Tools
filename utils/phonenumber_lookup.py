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

import time

import phonenumbers as p
from colorama import Style
from phonenumbers import carrier, geocoder, timezone

from helper import printer, timer


@timer.timer(require_input=True)
def lookup(phone_number: str) -> None:
    """
    Looks up for the information of a given phone number.

    :param phone_number: The phone number.
    """
    try:
        ph_no = p.parse(phone_number)
        country = p.region_code_for_country_code(ph_no.country_code)
        no_carrier = carrier.name_for_number(ph_no, "en")
        no_valid = p.is_valid_number(ph_no)
        no_possible = p.is_possible_number(ph_no)
        time_zone = timezone.time_zones_for_number(ph_no)
        region = geocoder.description_for_number(ph_no, "en")

        printer.info(
            f"Trying to find information about {Style.BRIGHT}{ph_no}{Style.RESET_ALL}..."
        )
        time.sleep(1)
        printer.success("Phone Number -", ph_no)
        printer.success("Valid Number -", no_valid)
        printer.success("Possible Number -", no_possible)
        printer.success("Sim Provider -", no_carrier)
        printer.success("Country -", country)
        printer.success("Region -", region)
        printer.success("Time Zone -", time_zone)
    except Exception as e:
        printer.error("Error : ", e)
