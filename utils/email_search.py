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

import time
import subprocess
from helper import printer, timer
from colorama import Style

class Holehe:
    """
    Searches for the email address in various websites using holehe.

    Thanks to Holehe, https://github.com/megadose/holehe

    :param email: The email address to search for.
    """
    @timer.timer
    def __init__(self, email) -> None:
        printer.info(f"Trying to find sites where {Style.BRIGHT}{email}{Style.RESET_ALL} is used, thanks to holehe.")
        try:
            result = subprocess.run(["holehe", email], capture_output=True, text=True, check=True)
            output = self._format_output(result.stdout)
            if output:
                printer.nonprefix(output)
                printer.nonprefix("Credits to megadose (Palenath) for holehe.")
            else:
                printer.error("No results found..!")
        except FileNotFoundError:
            printer.error(f"Error : {Style.BRIGHT}holehe{Style.RESET_ALL} was not found or it isn't in the PATH. Please make sure you have holehe installed and in your PATH.")
            printer.error(f"You can install holehe by executing {Style.BRIGHT}pip install holehe{Style.RESET_ALL}.")
        except subprocess.CalledProcessError as e:
            printer.error(f"Error : {e}")
        except Exception as e:
            printer.error(f"Unexpected error : {e}")

    @staticmethod
    def _format_output(output) -> str:
        lines = output.split("\n")[4:-4]
        for i, line in enumerate(lines):
            if "[+]" in line:
                lines[i] = f"\033[92m{line}\033[0m"
            elif "[-]" in line:
                lines[i] = f"\033[91m{line}\033[0m"
            elif "[x]" in line:
                lines[i] = f"\033[93m{line}\033[0m"
        return "\n".join(lines)
