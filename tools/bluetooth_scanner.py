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


class BluetoothScannerTool(BaseTool):
    id = "bluetooth_scanner"
    name = "Bluetooth Scanner"
    order = 15
    aliases = ("--bluetooth", "--bluetooth-scanner")
    description = "Scans for nearby Bluetooth devices via bluetoothctl on Linux and reports device names and MAC addresses."
    arguments = (
        ToolArgument("duration", "SECONDS", "Run Bluetooth scanner for SECONDS."),
    )

    def run(self, duration: int | str | None = None) -> None:
        from utils import bluetooth_scanner

        scan_duration = int(
            duration
            if duration is not None
            else printer.user_input("Enter a scan duration (seconds) : \t")
        )
        bluetooth_scanner.scan_nearby_bluetooth(duration=scan_duration)
