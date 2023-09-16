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
import psutil
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
                user_info_list = []

                for user in psutil.users():
                    username = user.name
                    terminal = user.terminal
                    host = user.host
                    started = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(user.started))
                    pid = user.pid

                    user_info = {
                        'Username': username,
                        'Terminal': terminal,
                        'Host': host,
                        'Started': started,
                        'PID': pid
                    }

                    user_info_list.append(user_info)

                # Iterate through the user information list to print the information
                for user_info in user_info_list:
                    printer.success("User Information:")
                    printer.success(f"Username: {user_info['Username']}")
                    printer.success(f"Terminal: {user_info['Terminal']}")
                    printer.success(f"Host: {user_info['Host']}")
                    printer.success(f"Started: {user_info['Started']}")
                    printer.success(f"PID: {user_info['PID']}", "\n")
            except Exception as e:
                printer.error("Error retrieving account information:", str(e))

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

