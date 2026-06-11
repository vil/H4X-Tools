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


class IpLookupTool(BaseTool):
    id = "ip_lookup"
    name = "IP Lookup"
    order = 4
    aliases = ("--ip", "--ip-lookup")
    description = (
        "Resolves a hostname or IP and queries ipinfo.io for geolocation, ISP/organization, postal code, timezone, "
        "and an OpenStreetMap link."
    )
    arguments = (ToolArgument("ip", "IP_OR_DOMAIN", "Run IP/domain lookup."),)

    def run(self, ip: str | None = None) -> None:
        from utils import ip_lookup

        ip = str(ip or printer.user_input("Enter a IP address OR domain : \t"))
        ip_lookup.lookup(ip_address=ip)
