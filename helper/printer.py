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

from colorama import Fore, Style


def print_colored(message, color, prefix, *args, **kwargs) -> None:
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
    print_colored(message, Fore.LIGHTBLUE_EX, "[*]", *args, **kwargs)


def success(message, *args, **kwargs) -> None:
    print_colored(message, Fore.LIGHTGREEN_EX, "[+]", *args, **kwargs)


def error(message, *args, **kwargs) -> None:
    print_colored(message, Fore.LIGHTRED_EX, "[!]", *args, **kwargs)


def warning(message, *args, **kwargs) -> None:
    print_colored(message, Fore.LIGHTYELLOW_EX, "[-]", *args, **kwargs)


def debug(message, *args, **kwargs) -> None:
    print_colored(message, Fore.LIGHTMAGENTA_EX, "[>]", *args, **kwargs)


def nonprefix(message, *args, **kwargs) -> None:
    print(message, *args, **kwargs)


def inp(prompt, *args, **kwargs) -> None:
    print_colored(prompt, Fore.LIGHTBLUE_EX, "[?]", end="", *args, **kwargs)
    return input()