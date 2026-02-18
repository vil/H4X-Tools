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

import getpass
import os
import subprocess
import time

from helper import printer, timer


@timer.timer(require_input=True)
def scan_for_local_users() -> None:
    """
    Scans for local accounts on the system and their information.
    """

    match os.name:
        case "nt":
            import psutil

            printer.info("Windows system detected.")

            try:
                user_info_list = []

                for user in psutil.users():
                    username = user.name
                    terminal = user.terminal
                    host = user.host
                    started = time.strftime(
                        "%m/%d/%Y %H:%M:%S", time.localtime(user.started)
                    )
                    pid = user.pid

                    # Get additional information using subprocess
                    user_sid = (
                        subprocess.check_output(
                            ["wmic", "useraccount", "get", "sid", "/value"]
                        )
                        .decode("utf-8")
                        .strip()
                    )
                    user_domain = (
                        subprocess.check_output(
                            ["wmic", "useraccount", "get", "domain", "/value"]
                        )
                        .decode("utf-8")
                        .strip()
                    )

                    user_info_list.append(
                        {
                            "Username": username,
                            "Terminal": terminal,
                            "Host": host,
                            "Started": started,
                            "PID": pid,
                            "SID": user_sid,
                            "Domain": user_domain,
                        }
                    )

                printer.noprefix("")
                printer.section("Local User Accounts")

                for user_info in user_info_list:
                    printer.success(f"Username : {user_info['Username']}")
                    printer.success(f"Terminal : {user_info['Terminal']}")
                    printer.success(f"Host     : {user_info['Host']}")
                    printer.success(f"Started  : {user_info['Started']}")
                    printer.success(f"PID      : {user_info['PID']}")
                    printer.success(f"SID      : {user_info['SID']}")
                    printer.success(f"Domain   : {user_info['Domain']}")
                    printer.noprefix("")

            except Exception as e:
                printer.error(f"Error retrieving account information: {e}")

        case "posix":
            import grp
            import pwd

            printer.info("Linux system detected.")

            try:
                user_info_list = []

                login_name = getpass.getuser()

                for user in pwd.getpwall():
                    username = user.pw_name
                    uid = user.pw_uid
                    gid = user.pw_gid
                    full_name = user.pw_gecos
                    home_dir = user.pw_dir
                    shell = user.pw_shell

                    # Get additional information using grp
                    group_name = grp.getgrgid(gid)[0]

                    user_info_list.append(
                        {
                            "Username": username,
                            "UID": uid,
                            "GID": gid,
                            "Full Name": full_name,
                            "Home Directory": home_dir,
                            "Shell": shell,
                            "Group Name": group_name,
                            "Login Name": login_name,
                        }
                    )

                printer.noprefix("")
                printer.section("Local User Accounts")

                for user_info in user_info_list:
                    printer.success(f"Username       : {user_info['Username']}")
                    printer.success(f"UID            : {user_info['UID']}")
                    printer.success(f"GID            : {user_info['GID']}")
                    printer.success(f"Full Name      : {user_info['Full Name']}")
                    printer.success(f"Home Directory : {user_info['Home Directory']}")
                    printer.success(f"Shell          : {user_info['Shell']}")
                    printer.success(f"Group Name     : {user_info['Group Name']}")
                    printer.success(f"Login Name     : {user_info['Login Name']}")
                    printer.noprefix("")

            except Exception as e:
                printer.error(f"Error retrieving account information: {e}")

        case _:
            printer.error("Unsupported platform..!")
