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


class WhoisLookupTool(BaseTool):
    id = "whois_lookup"
    name = "WhoIs Lookup"
    order = 9
    aliases = ("--whois", "--whois-lookup")
    description = "Performs a WHOIS query on a domain and displays registrar, registration/expiry dates, name servers, status, and registrant details."
    arguments = (ToolArgument("domain", "DOMAIN", "Run WHOIS lookup for DOMAIN."),)

    def run(self, domain: str | None = None) -> None:
        from utils import whois_lookup

        domain = str(domain or printer.user_input("Enter a domain : \t"))
        whois_lookup.check_whois(domain=domain)
