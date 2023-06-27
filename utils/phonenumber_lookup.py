"""
 Copyright (c) 2022 GNU GENERAL PUBLIC

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

import phonenumbers as p
from phonenumbers import geocoder
from phonenumbers import carrier
from helper import printer
import time


class LookUp:
    """
    Looks up for the information of a given phone number.

    :param no: The phone number.
    """
    def __init__(self, no):
        print("\n")
        try:
            ph_no = p.parse(no)
            geo_location = geocoder.description_for_number(ph_no, 'en')
            no_carrier = carrier.name_for_number(ph_no, 'en')
            no_valid = p.is_valid_number(ph_no)
            no_possible = p.is_possible_number(ph_no)
            printer.info(f"Trying to find the information of '{no}'")
            time.sleep(1)
            printer.success(f"Valid Number -", no_valid)
            printer.success(f"Possible Number -", no_possible)
            printer.success(f"Country -", geo_location)
            printer.success(f"Sim Provider -", no_carrier)
            printer.success("\n")
        except Exception as e:
            printer.error(f"Error : ", e)
            pass
