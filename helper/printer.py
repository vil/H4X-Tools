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

from colorama import Fore, Style


def print_colored(message, color, prefix, *args, **kwargs):
    """
    Print colored message with specified color and prefix.

    :param message: message to print
    :param color: color code from colorama.Fore
    :param prefix: prefix for the message
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(f"{color}{prefix} {message}{Style.RESET_ALL}", *args, **kwargs)


def info(message, *args, **kwargs):
    print_colored(message, Fore.BLUE, "[*]", *args, **kwargs)


def success(message, *args, **kwargs):
    print_colored(message, Fore.GREEN, "[+]", *args, **kwargs)


def error(message, *args, **kwargs):
    print_colored(message, Fore.RED, "[!]", *args, **kwargs)


def warning(message, *args, **kwargs):
    print_colored(message, Fore.YELLOW, "[-]", *args, **kwargs)


def debug(message, *args, **kwargs):
    print_colored(message, Fore.MAGENTA, "[$]", *args, **kwargs)


def nonprefix(message, *args, **kwargs):
    print(message, *args, **kwargs)
