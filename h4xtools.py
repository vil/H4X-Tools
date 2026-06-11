#!/usr/bin/env python3

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

import argparse
import socket
import time

from colorama import Fore, Style

from helper import config, printer
from tools import BaseTool, discover_tools

VERSION = "26.1"
QUIT_COMMANDS = {"quit", "exit", "q", "kill"}
HELP_COMMANDS = {"?", "help"}


def _internet_check() -> None:
    """
    Check if the user is connected to the internet by
    creating a socket connection to a known host and port.
    """
    try:
        socket.setdefaulttimeout(3)
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
    except socket.error as sock_error:
        printer.warning(
            "Internet Connection is Unavailable or some other problem occurred..!\n{}".format(
                sock_error
            )
        )


def _print_banner() -> None:
    print(
        Fore.LIGHTBLACK_EX
        + f"""
 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀
{Style.RESET_ALL}v{VERSION} / Vili (@vil) - https://vili.dev
    """
    )


def _display_help(tools: tuple[BaseTool, ...]) -> None:
    print(Fore.LIGHTCYAN_EX)
    print(
        "H4X-Tools v{} - A modular, terminal-based toolkit for OSINT, reconnaissance, and scraping - built in Python, runs on Linux and Windows.".format(
            VERSION
        )
    )
    print("Repository link: https://github.com/vil/h4x-tools")
    print("\nMade in Finland, with love.\n")

    print("Available Tools:")
    print("------------------")
    for index, tool in enumerate(tools, start=1):
        aliases = ", ".join(tool.aliases)
        print(f"* {str(index).zfill(2)}. {tool.name} ({aliases}) - {tool.description}")

    print("\nAdding Tools:")
    print("------------------")
    print(
        "Create a Python file in tools/, subclass tools.base.BaseTool, set id/name/description/order/aliases/arguments, "
        "and implement run(). H4X-Tools discovers it automatically at startup."
    )

    print("\nClosing the Toolkit:")
    print("----------------------")
    print("You can close the toolkit using the following commands:")
    for command in sorted(QUIT_COMMANDS):
        print(f"* {command}")

    print("\nLicense and Credits:")
    print("---------------------")
    print(
        "H4X-Tools is under the GNU General Public License v3, made by Vili (@vil).\n"
        "This toolkit is for educational and authorised security research purposes only."
    )


def _print_menu(tools: tuple[BaseTool, ...]) -> None:
    max_option_length = max(len(tool.name) for tool in tools)

    for index, tool in enumerate(tools, start=1):
        key = str(index)
        print(
            f"{Fore.LIGHTGREEN_EX}[{key.zfill(2)}]{Style.RESET_ALL} {tool.name.ljust(max_option_length)}",
            end="",
        )

        if index % 2 == 0:
            print()
        else:
            print(" " * 4, end="")

    print("\n")
    print(f"Type {Style.BRIGHT}?{Style.RESET_ALL} for help.")
    print(f"Type {Style.BRIGHT}exit{Style.RESET_ALL} to close the toolkit...")


def _build_parser(tools: tuple[BaseTool, ...]) -> argparse.ArgumentParser:
    """
    Build the H4X-Tools command-line parser from discovered tool metadata.

    :return: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="h4xtools",
        description="H4X-Tools - modular OSINT, reconnaissance, and scraping toolkit.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=f"H4X-Tools v{VERSION}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Enable verbose output. Repeat for more verbosity.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output. Implies verbose output.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Print the full tool help and exit.",
    )
    parser.add_argument(
        "--no-internet-check",
        action="store_true",
        help="Skip the startup internet connectivity check.",
    )

    tool_group = parser.add_argument_group(
        "Tool shortcuts",
        "Pass one or more tool flags to run them directly without opening the menu. "
        "Flags with optional values will prompt if the value is omitted.",
    )
    for tool in tools:
        tool.add_cli_arguments(tool_group)

    return parser


def _cli_tool_selected(args: argparse.Namespace, tools: tuple[BaseTool, ...]) -> bool:
    """
    Determine whether any direct-run tool flag was provided.

    :param args: Parsed CLI args.
    :param tools: Discovered tools.
    :return: ``True`` if at least one tool should run directly.
    """
    return any(tool.selected(args) for tool in tools)


def _run_cli_tools(args: argparse.Namespace, tools: tuple[BaseTool, ...]) -> None:
    """
    Execute tool flags directly and exit without opening the menu.

    Tools run in menu order when multiple flags are provided.

    :param args: Parsed CLI args.
    :param tools: Discovered tools.
    """
    for tool in tools:
        if not tool.selected(args):
            continue

        try:
            printer.verbose(f"Running {tool.name}")
            tool.run_from_cli(args)
        except KeyboardInterrupt:
            printer.warning("Cancelled..!")
            break


def main(args: argparse.Namespace | None = None) -> None:
    tools = discover_tools()

    if args is None:
        args = _build_parser(tools).parse_args()

    printer.set_verbosity(verbose=args.verbose > 0, debug_enabled=args.debug)
    config.init_config()

    if args.list_tools:
        _display_help(tools)
        return

    if not args.no_internet_check:
        _internet_check()
        time.sleep(0.5)

    printer.debug("DEBUG IS ON.")

    if _cli_tool_selected(args, tools):
        printer.set_pause_after_tool(False)
        _run_cli_tools(args, tools)
        return

    printer.set_pause_after_tool(True)
    menu_options = {str(index): tool for index, tool in enumerate(tools, start=1)}

    while True:
        _print_banner()
        _print_menu(tools)
        user_input = printer.user_input("Tool to execute : \t")
        normalized_input = user_input.lower()

        if normalized_input in QUIT_COMMANDS:
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            time.sleep(0.5)
            break

        if user_input in menu_options:
            try:
                menu_options[user_input].run()
            except KeyboardInterrupt:
                printer.warning("Cancelled..!")
        elif normalized_input in HELP_COMMANDS:
            _display_help(tools)
            printer.user_input("Done reading? Press the Enter key.")
        else:
            printer.error("Invalid option!")
            time.sleep(0.5)


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except ValueError:
            printer.error("Invalid value inputted..!")
        except KeyboardInterrupt:
            print("\n")
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            exit(0)
