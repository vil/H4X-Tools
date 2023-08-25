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

import socket
from helper import printer, timer
from concurrent.futures import ThreadPoolExecutor, as_completed

open_ports = []
failed_ports = []


class Scan:
    """
    Scans for open ports in a given IP address.

    :param ip: IP address.
    :param port_range: The range of ports to scan.
    """
    @timer.timer
    def __init__(self, ip, port_range):
        try:
            printer.info(f"Scanning for open ports in '{ip}' with range of '1-{port_range}'..!")
            printer.warning("This may take a while..!")
            self.scan(ip, port_range)
            if len(open_ports) == 0:
                printer.error(f"No open ports found in '{ip}'..!")
            else:
                printer.success(f"Found {len(open_ports)}/{len(failed_ports)} open ports in '{ip}'..!")
        except KeyboardInterrupt:
            printer.error("Cancelled..!")

    def scan(self, ip, port_range):
        """
        Scans for open ports in a given IP address.

        :param ip: IP address.
        :param port_range: The range of ports to scan.
        """
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.scan_port, ip, port): port for port in range(1, port_range + 1)}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    printer.success(result)

    @staticmethod
    def scan_port(ip, port):
        """
        Scans an individual port of a given IP address.

        :param ip: IP address.
        :param port: Port number.
        :return: Success message if port is open, None otherwise.
        """
        try:
            with socket.socket() as sock:
                sock.settimeout(0.5)
                sock.connect((str(ip), port))
                open_ports.append(port)
                return printer.success(f"Port '{port}' is open on '{ip}'..!")
        except socket.timeout:
            failed_ports.append(port)
        except ConnectionRefusedError:
            return None
        except socket.error as e:
            return printer.error(f"An error occurred while scanning port '{port}' on '{ip}' : {str(e)}..!")
