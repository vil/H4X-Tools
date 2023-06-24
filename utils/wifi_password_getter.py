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

import os
import subprocess
import re
from helper import printer
import time


class Scan:
    """
    Scans for the saved Wi-Fi passwords on the system.
    """

    def __init__(self):
        if os.name == "nt":
            printer.info("Windows system detected..!")
            time.sleep(1)

            output = subprocess.check_output("netsh wlan show profile", shell=True).decode("utf-8")
            profiles = output.split("User Profile")[1:]

            for profile in profiles:
                profile_name = profile.split(":")[1].strip()
                printer.success("Wi-Fi Name: ", profile_name)

                try:
                    wifi_info = subprocess.check_output(
                        'netsh wlan show profile name="' + profile_name + '" key=clear', shell=True
                    ).decode("utf-8")

                    password_index = wifi_info.find("Key Content")
                    if password_index != -1:
                        password_start = password_index + len("Key Content") + 2
                        password = wifi_info[password_start:].split("\r\n")[0].strip()
                        printer.success("Wi-Fi Password: ", password, "\n")
                    else:
                        printer.warning("No Wi-Fi password found.")
                except subprocess.CalledProcessError as e:
                    printer.error("Error retrieving Wi-Fi information: ", str(e))
                    pass

        else:
            printer.info(f"Linux system detected..!\n")
            time.sleep(1)
            try:
                output = subprocess.check_output(['nmcli', '-f', 'NAME,UUID', 'connection', 'show', '--active'])
                connections = re.findall(r'(\S+)\s+([0-9a-f-]{36})', output.decode())
                for ssid, uuid in connections:
                    password_output = subprocess.check_output(
                        ['nmcli', '-s', '-g', '802-11-wireless-security.psk', 'connection', 'show', uuid])
                    password = password_output.decode().strip()
                    printer.success(f"SSID: {ssid}\nPassword: {password}\n")

            except OSError as e:
                printer.error("Is your system using nmcli?")
                printer.error(f"Error : ", e)
                pass
