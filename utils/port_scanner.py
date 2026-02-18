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

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def scan(ip: str, port_range: int) -> None:
    """
    Scans for open ports in a given IP address.

    :param ip: IP address.
    :param port_range: The range of ports to scan.
    """
    # Initialise fresh state for each run so consecutive scans don't accumulate.
    open_ports: list[int] = []
    failed_ports: list[int] = []

    try:
        printer.info(
            f"Scanning for open ports for {Style.BRIGHT}{ip}{Style.RESET_ALL} "
            f"with the port range of {Style.BRIGHT}1-{port_range}{Style.RESET_ALL}..."
        )
        if port_range > 1000:
            printer.warning("This may take a while...")

        printer.noprefix("")
        printer.section("Port Scan Results")

        _scan_ports(ip, port_range, open_ports, failed_ports)

        printer.noprefix("")
        if not open_ports:
            printer.error(
                f"No open ports found for {Style.BRIGHT}{ip}{Style.RESET_ALL}..!"
            )
        else:
            printer.success(
                f"Found {len(open_ports)} open port(s) out of "
                f"{len(open_ports) + len(failed_ports)} scanned on {ip}."
            )
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
    except RecursionError:
        printer.error("Unexpected recursion error.")


def _scan_ports(
    ip: str,
    port_range: int,
    open_ports: list[int],
    failed_ports: list[int],
) -> None:
    """
    Scans for open ports in a given IP address using a thread pool.

    :param ip: IP address.
    :param port_range: The range of ports to scan.
    :param open_ports: List to collect open port numbers into.
    :param failed_ports: List to collect closed/timed-out port numbers into.
    """
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(_connect_to_port, ip, port, open_ports, failed_ports): port
            for port in range(1, port_range + 1)
        }
        for future in as_completed(futures):
            # Exceptions are already handled inside connect_to_port; just drain results.
            future.result()


def _connect_to_port(
    ip: str,
    port: int,
    open_ports: list[int],
    failed_ports: list[int],
) -> None:
    """
    Attempts to connect to a single port on the given IP address.
    Records the result in open_ports or failed_ports accordingly.

    :param ip: IP address.
    :param port: Port number.
    :param open_ports: Shared list to append open ports to.
    :param failed_ports: Shared list to append failed ports to.
    """
    try:
        with socket.socket() as sock:
            sock.settimeout(0.5)
            sock.connect((ip, port))
            open_ports.append(port)
            printer.success(f"Port {Style.BRIGHT}{port}{Style.RESET_ALL}/TCP is open")
    except socket.timeout:
        failed_ports.append(port)
    except ConnectionRefusedError:
        failed_ports.append(port)
    except socket.error as e:
        printer.error(
            f"An error occurred while scanning port {Style.BRIGHT}{port}{Style.RESET_ALL} "
            f"for {Style.BRIGHT}{ip}{Style.RESET_ALL} : {e}"
        )
