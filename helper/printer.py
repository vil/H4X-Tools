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

import re
import sys

from colorama import Fore, Style

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _print_colored(message: str, color: str, prefix: str, *args, **kwargs) -> None:
    """
    Print colored message with specified color and prefix.

    :param message: message to print
    :param color: color code from colorama.Fore
    :param prefix: prefix for the message
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(f"{color}{prefix}{Style.RESET_ALL} {message}", *args, **kwargs)


def info(message, *args, **kwargs) -> None:
    _print_colored(message, Fore.LIGHTBLUE_EX, "[*]", *args, **kwargs)


def success(message, *args, **kwargs) -> None:
    _print_colored(message, Fore.LIGHTGREEN_EX, "[+]", *args, **kwargs)


def error(message, *args, **kwargs) -> None:
    _print_colored(message, Fore.LIGHTRED_EX, "[!]", *args, **kwargs)


def warning(message, *args, **kwargs) -> None:
    _print_colored(message, Fore.LIGHTYELLOW_EX, "[-]", *args, **kwargs)


def debug(message, *args, **kwargs) -> None:
    if "--debug" in sys.argv:
        _print_colored(message, Fore.LIGHTMAGENTA_EX, "[>]", *args, **kwargs)


def section(title: str) -> None:
    """
    Print a consistently formatted section header.

    Output looks like:
        [*] ─── Title ──────────────────────────────────────

    The total content width (after the ``[*] `` prefix) is always 50 characters,
    regardless of the title length.

    :param title: The section title to display.
    """
    _TOTAL = 50
    left = "─── "
    fill = _TOTAL - len(left) - len(title) - 1
    right = " " + "─" * max(fill, 3)
    _print_colored(left + title + right, Fore.LIGHTBLUE_EX, "[*]")


def noprefix(message, *args, **kwargs) -> None:
    print(message, *args, **kwargs)


def user_input(prompt, *args, **kwargs) -> str:
    _print_colored(prompt, Fore.LIGHTBLUE_EX, "[?]", end="", *args, **kwargs)
    return input()


def ansi_escape(output: str) -> str:
    """
    Strips ANSI escapes from output.

    :retrun clean_output: ANSI escape stripped output.
    """
    clean_output = ANSI_ESCAPE.sub("", output)

    return clean_output
