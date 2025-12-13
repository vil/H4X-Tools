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

import re
import subprocess

from colorama import Style

from helper import printer, timer


@timer.timer(require_input=True)
def search(email: str) -> None:
    """
    Searches for the email address in various websites using holehe.

    Thanks to Holehe, https://github.com/megadose/holehe

    :param email: The email address to search for
    """
    printer.info(
        f"Trying to find sites where {Style.BRIGHT}'{email}'{Style.RESET_ALL} has been registered:"
    )
    try:
        result = subprocess.run(
            ["holehe", email], capture_output=True, text=True, check=True
        )

        if result:
            print_output(result.stdout)
            printer.info("Credits to megadose (Palenath) for holehe.")
        else:
            printer.error("No results.")

    except FileNotFoundError:
        printer.error(
            f"Error : {Style.BRIGHT}holehe{Style.RESET_ALL} was not found or it isn't in the PATH. Please make sure you have holehe installed and in your PATH."
        )
        printer.error(
            f"You can install holehe by executing {Style.BRIGHT}pip install holehe{Style.RESET_ALL}."
        )
    except subprocess.CalledProcessError as e:
        printer.error(f"Error : {e}")
    except Exception as e:
        printer.error(f"Unexpected error : {e}")


def print_output(output: str) -> None:
    """Format and print Holehe's output"""
    # Remove top/bottom decoration lines, keep only content
    lines = output.split("\n")

    for line in lines:
        clean_line = printer.ansi_escape(line).strip()

        # Skip decorative lines, email and footer
        if (
            clean_line.startswith("***")
            or "@" in clean_line
            or clean_line.startswith("[+] Email used")
        ):
            continue

        # Match patterns like:  [x] adobe.com
        match = re.match(r"^\[(\+|\-|x)\]\s*(.+)$", clean_line)
        if not match:
            continue

        symbol, site = match.groups()

        # Call appropriate printer method
        if symbol == "+":
            printer.success(site)
        elif symbol == "-":
            printer.error(site)
        elif symbol == "x":
            printer.warning(site)
