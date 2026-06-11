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


class PortScannerTool(BaseTool):
    id = "port_scanner"
    name = "Port Scanner"
    order = 8
    aliases = ("--port", "--port-scanner")
    description = "Concurrently scans a user-defined TCP port range on any IP or hostname using a 50-thread pool."
    arguments = (
        ToolArgument("ip", "IP_OR_DOMAIN", "Run port scanner for IP_OR_DOMAIN."),
        ToolArgument(
            "port_range",
            "PORTS",
            "Number of ports to scan when using --port/--port-scanner.",
            flags=("--port-range",),
            parser_type=int,
        ),
    )

    def run(self, ip: str | None = None, port_range: int | str | None = None) -> None:
        from utils import port_scanner

        ip = str(ip or printer.user_input("Enter a IP address OR domain : \t"))
        port_range = int(
            port_range
            if port_range is not None
            else printer.user_input("Enter number of ports to scan : \t")
        )
        port_scanner.scan(ip=ip, port_range=port_range)
