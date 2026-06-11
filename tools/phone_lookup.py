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

from helper import printer
from tools.base import BaseTool, ToolArgument


class PhoneLookupTool(BaseTool):
    id = "phone_lookup"
    name = "Phone Lookup"
    order = 3
    aliases = ("--phone", "--phone-lookup")
    description = (
        "Validates and analyses a phone number, including country, region, carrier, line type, and time zones, "
        "then checks social-media platform registrations."
    )
    arguments = (
        ToolArgument("phone_number", "NUMBER", "Run phone lookup for NUMBER."),
    )

    def run(self, phone_number: str | None = None) -> None:
        from utils import phonenumber_lookup

        printer.info("Include the country code, e.g. +358501234567 or +12025550123")
        phone_number = str(
            phone_number
            or printer.user_input("Enter a phone-number with country code : \t")
        )
        phonenumber_lookup.lookup(phone_number=phone_number)
