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

from colorama import Fore


def info(message, *args, **kwargs):
    """
    Print info message with blue color.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(Fore.BLUE + "[*] " + message, Fore.RESET, *args, **kwargs)


def success(message, *args, **kwargs):
    """
    Print success message with green color.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(Fore.GREEN + "[+] " + message, Fore.RESET, *args, **kwargs)


def error(message, *args, **kwargs):
    """
    Print error message with red color.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(Fore.RED + "[!] " + message, Fore.RESET, *args, **kwargs)


def warning(message, *args, **kwargs):
    """
    Print warning message with yellow color.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(Fore.YELLOW + "[-] " + message, Fore.RESET, *args, **kwargs)


def debug(message, *args, **kwargs):
    """
    Print debug message with magenta color.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(Fore.MAGENTA + "[$] " + message, Fore.RESET, *args, **kwargs)


def nonprefix(message, *args, **kwargs):
    """
    Print message without prefix.

    :param message: message to print
    :param args: arguments if any
    :param kwargs: keyword arguments if any
    """
    print(message, *args, **kwargs)
