"""
 Copyright (c) 2023-2025. Vili and contributors.

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
from colorama import Style

open_ports = []
failed_ports = []


class Scan:
    """
    Scans for open ports in a given IP address.

    :param ip: IP address.
    :param port_range: The range of ports to scan.
    """
    @timer.timer
    def __init__(self, ip, port_range) -> None:
        try:
            printer.info(f"Scanning for open ports for {Style.BRIGHT}{ip}{Style.RESET_ALL} with the port range of {Style.BRIGHT}1-{port_range}{Style.RESET_ALL}...")
            if port_range > 1000:
                printer.warning("This may take a while...")
            self.scan(ip, port_range)
            if len(open_ports) == 0:
                printer.error(f"No open ports found for {Style.BRIGHT}{ip}{Style.RESET_ALL}..!")
            else:
                printer.success(f"Found {len(open_ports)}/{len(failed_ports)} open ports in '{ip}'..!")
        except KeyboardInterrupt:
            printer.error("Cancelled..!")

    def scan(self, ip, port_range) -> None:
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
    def scan_port(ip, port) -> None:
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
                return printer.success(f"Found a open port : {Style.BRIGHT}{port}{Style.RESET_ALL}")
        except socket.timeout:
            failed_ports.append(port)
        except ConnectionRefusedError:
            return None
        except socket.error as e:
            return printer.error(f"An error occurred while scanning port {Style.BRIGHT}{port}{Style.RESET_ALL} for {Style.BRIGHT}{ip}{Style.RESET_ALL} : {str(e)}")
