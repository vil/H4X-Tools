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
import re
import subprocess

from helper import printer, timer


@timer.timer(require_input=True)
def get_local_passwords() -> None:
    """Retrieves saved Wi-Fi passwords on the system."""
    match os.name:
        case "nt":
            printer.info("Windows system detected.")
            try:
                output = subprocess.check_output(
                    "netsh wlan show profiles", shell=True
                ).decode("utf-8")
                profile_names = [
                    line.split(":")[1].strip()
                    for line in output.splitlines()
                    if "All User Profile" in line
                ]

                printer.noprefix("")
                printer.section("Saved Wi-Fi Passwords")

                for profile_name in profile_names:
                    try:
                        wifi_info = subprocess.check_output(
                            'netsh wlan show profile name="{}" key=clear'.format(
                                profile_name
                            ),
                            shell=True,
                        ).decode("utf-8")

                        password_index = wifi_info.find("Key Content")
                        if password_index != -1:
                            password_start = password_index + len("Key Content") + 2
                            password = (
                                wifi_info[password_start:].split("\r\n")[0].strip()
                            )
                            printer.success(f"Network  : {profile_name}")
                            printer.success(f"Password : {password}")
                        else:
                            printer.success(f"Network  : {profile_name}")
                            printer.warning("Password : (none saved)")
                        printer.noprefix("")
                    except subprocess.CalledProcessError as e:
                        printer.error(
                            f"Error retrieving Wi-Fi info for {profile_name} : {e}"
                        )
            except subprocess.CalledProcessError as e:
                printer.error(f"Error retrieving profile names : {e}")

        case "posix":
            printer.info("Linux system detected.")
            try:
                output = subprocess.check_output(
                    ["nmcli", "-f", "NAME,UUID", "connection", "show"]
                )
                connections = re.findall(r"(\S+)\s+([0-9a-f-]{36})", output.decode())

                printer.noprefix("")
                printer.section("Saved Wi-Fi Passwords")

                for ssid, uuid in connections:
                    try:
                        password_output = subprocess.check_output(
                            [
                                "nmcli",
                                "-s",
                                "-g",
                                "802-11-wireless-security.psk",
                                "connection",
                                "show",
                                uuid,
                            ]
                        )
                        password = password_output.decode().strip()

                        printer.success(f"Network  : {ssid}")
                        printer.success(f"Password : {password}")
                        printer.noprefix("")
                    except subprocess.CalledProcessError as e:
                        printer.error(f"Error retrieving password for {ssid} : {e}")

            except subprocess.CalledProcessError as e:
                printer.error(f"Error retrieving saved connections : {e}")
                printer.error("Is your system using nmcli?")

        case _:
            printer.error("Unsupported platform..!")
