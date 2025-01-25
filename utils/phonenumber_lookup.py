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
from phonenumbers import carrier, geocoder, timezone
from helper import printer, timer
from colorama import Style

class LookUp:
    """
    Looks up for the information of a given phone number.

    :param no: The phone number.
    """
    @timer.timer
    def __init__(self, no) -> None:
        try:
            ph_no = p.parse(no)
            country = p.region_code_for_country_code(ph_no.country_code)
            no_carrier = carrier.name_for_number(ph_no, "en")
            no_valid = p.is_valid_number(ph_no)
            no_possible = p.is_possible_number(ph_no)
            time_zone = timezone.time_zones_for_number(ph_no)
            region = geocoder.description_for_number(ph_no, "en")

            printer.info(f"Trying to find information about {Style.BRIGHT}{no}{Style.RESET_ALL}...")
            time.sleep(1)
            printer.success("Phone Number -", no)
            printer.success(f"Valid Number -", no_valid)
            printer.success(f"Possible Number -", no_possible)
            printer.success(f"Sim Provider -", no_carrier)
            printer.success(f"Country -", country)
            printer.success(f"Region -", region)
            printer.success(f"Time Zone -", time_zone)
        except Exception as e:
            printer.error(f"Error : ", e)
