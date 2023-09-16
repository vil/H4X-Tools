"""
 Copyright (c) 2023. Vili and contributors.

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
from helper import printer, timer


class Scan:
    """
    Scans for local accounts on the system and their information.
    """
    @timer.timer
    def __init__(self):
        if os.name == "nt":
            printer.info("Windows system detected..!\n")
            time.sleep(1)
            try:
                output = subprocess.check_output("net user", shell=True).decode("utf-8")
                profile_names = [line.split(":")[1].strip() for line in output.splitlines() if
                                 "All User Profile" in line]

                for profile_name in profile_names:
                    try:
                        wifi_info = subprocess.check_output(
                            'net user "{}"'.format(profile_name),
                            shell=True).decode("utf-8")

                        password_index = wifi_info.find("Password last set")
                        if password_index != -1:
                            password_start = password_index + len("Password last set") + 2
                            password = wifi_info[password_start:].split("\r\n")[0].strip()
                            printer.success("Account Name:", profile_name)
                            printer.success("Account Password:", password, "\n")
                        else:
                            printer.success("Account Name:", profile_name)
                            printer.warning("No account password found. It might be empty.\n")
                    except subprocess.CalledProcessError as e:
                        printer.error("Error retrieving account information:", str(e))
            except subprocess.CalledProcessError as e:
                printer.error("Error retrieving profile names:", str(e))

        else:
            printer.info("Linux system detected..!\n")
            time.sleep(1)
            try:
                user_info_list = []

                with open('/etc/passwd', 'r') as passwd_file:
                    for line in passwd_file:
                        fields = line.strip().split(':')
                        username = fields[0]
                        uid = fields[2]
                        gid = fields[3]
                        full_name = fields[4]
                        home_dir = fields[5]
                        shell = fields[6]

                        user_info = {
                            'Username': username,
                            'UID': uid,
                            'GID': gid,
                            'Full Name': full_name,
                            'Home Directory': home_dir,
                            'Shell': shell
                        }

                        user_info_list.append(user_info)

                printer.warning("You need root privileges to retrieve account passwords.\n")
                root_access = input("[$] Ask for root password? [y/n] ~> ").lower()

                if root_access == "y" or root_access == "yes":
                    # Ask for root password
                    subprocess.check_output("sudo -v", shell=True)
                    # Cat the /etc/shadow file as sudo to retrieve account passwords
                    subprocess.check_output("sudo cat /etc/shadow", shell=True)
                    # Iterate through the user information list to retrieve account passwords
                    for user_info in user_info_list:
                        try:
                            # Get the password from the /etc/shadow file
                            password = subprocess.check_output(
                                "sudo grep {} /etc/shadow | cut -d ':' -f 2".format(user_info['Username']),
                                shell=True).decode("utf-8").strip()
                            # Update the user information dictionary with the password
                            user_info['Password'] = password
                        except subprocess.CalledProcessError as e:
                            # If the password is empty, set it to N/A
                            user_info['Password'] = "N/A"
                else:
                    printer.warning("Skipping password retrieval...\n")
                    user_info['Password'] = "N/A"

                # Iterate through the user information list to print the information
                for user_info in user_info_list:
                    printer.success("Username:", user_info['Username'])
                    printer.success("UID:", user_info['UID'])
                    printer.success("GID:", user_info['GID'])
                    printer.success("Full Name:", user_info['Full Name'])
                    printer.success("Home Directory:", user_info['Home Directory'])
                    printer.success("Shell:", user_info['Shell'])
                    if root_access == "y" or root_access == "yes":
                        printer.success("Password:", user_info['Password'], "\n")
                    else:
                        printer.success("Password:", "N/A", "\n")
            except Exception as e:
                printer.error("Error retrieving account information:", str(e))

