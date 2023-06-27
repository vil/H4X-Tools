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

import socket
import time
from helper import printer


class Scan:
    """
    Scans for an IP address of a given website.

    :param ip: The website url.
    """
    def __init__(self, ip):
        try:
            ip_addr = socket.gethostbyname(ip)
            printer.info(f"Trying to find the IP address of '{ip}'")
            time.sleep(1)
            printer.success(f"IP address of the website : \t ", ip_addr)
        except Exception as e:
            printer.error(f"Error : ", e)
            pass
