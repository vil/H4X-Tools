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

import os
import subprocess
import time

from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def scan_nearby_bluetooth(duration: int) -> None:
    """
    Performs a basic scan for nearby Bluetooth devices.

    - Requires 'bluetoothctl' on Linux

    :param duration: amount of seconds to scan for
    """
    match os.name:
        case "nt":
            # TODO
            printer.warning("Sorry, this feature isn't ready yet..!")
        case "posix":
            _parse_output(output=_scan_linux(duration=duration), platform="linux")
        case _:
            printer.error("Unsupported platform..!")


def _scan_linux(duration: int) -> str:
    """
    Performs a bluetoothctl scan on Linux systems.

    :param duration: How many seconds to scan for.
    """
    printer.info(
        f"Linux system detected... Performing {Style.BRIGHT}bluetoothctl{Style.RESET_ALL} scan..."
    )

    output = ""

    try:
        process = subprocess.Popen(
            ["bluetoothctl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        if process.stdin is None:
            printer.error("Failed to open bluetoothctl stdin.")
            return output

        process.stdin.write("scan on\n")
        process.stdin.flush()

        time.sleep(duration)

        process.stdin.write("scan off\n")
        process.stdin.write("quit\n")
        process.stdin.flush()

        output, _ = process.communicate()

    except subprocess.CalledProcessError as e:
        printer.error(f"Error : {e.returncode} - {e.stderr}")
        printer.error(
            f"Is your system using {Style.BRIGHT}bluetoothctl{Style.RESET_ALL}?"
        )

    return output


def _scan_windows() -> None:
    """TODO"""
    return


def _parse_output(output: str, platform: str) -> None:
    match platform:
        case "windows":
            # Parse Windows output
            devices = []
            printer.error("Sorry, this feature isn't ready yet..!")

        case "linux":
            # Parse Linux output
            devices = []
            clean_output = printer.ansi_escape(output)

            for line in clean_output.splitlines():
                printer.debug(line)
                if "[NEW] Device" in line:
                    parts = line.split()
                    printer.debug(parts)
                    # parts[0] = [NEW]
                    # parts[1] = Device
                    # parts[2] = MAC address
                    # parts[3:] = device name (may contain spaces)
                    if len(parts) < 3:
                        continue
                    mac = parts[2]
                    name = " ".join(parts[3:]).strip() if len(parts) > 3 else "No Name"

                    devices.append({"mac": mac, "name": name, "raw": line})

            printer.noprefix("")
            printer.section("Nearby Bluetooth Devices")

            if not devices:
                printer.warning("No devices found.")
            else:
                for device in devices:
                    printer.success(f"Name : {device['name']}")
                    printer.success(f"MAC  : {device['mac']}")
                    printer.noprefix("")
        case _:
            printer.error("idk how u got here.")
