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
from tools.base import BaseTool


class WifiFinderTool(BaseTool):
    id = "wifi_finder"
    name = "Wi-Fi Finder"
    order = 12
    aliases = ("--wifi-finder",)
    description = "Scans for nearby Wi-Fi networks using netsh on Windows or nmcli on Linux, reporting SSID, signal strength, and security type."

    def run(self) -> None:
        from utils import wifi_finder

        printer.info("Scanning for nearby Wi-Fi networks...")
        wifi_finder.scan_nearby_wifi()
