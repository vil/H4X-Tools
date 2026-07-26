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
import subprocess
import sys
import time

from colorama import Fore, Style

from helper import config, printer, tui
from tools import BaseTool, discover_tools

QUIT_COMMANDS = {"quit", "exit", "q", "kill"}
HELP_COMMANDS = {"?", "help"}


def _get_git_ref() -> str:
    """Returns the SHORT commit hash of the latest commit."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        printer.verbose(
            "Failed to fetch the build hash! Make sure you are running this in the parent folder!"
        )
        return "26"


def _internet_check() -> None:
    """
    Check if the user is connected to the internet by
    creating a socket connection to a known host and port.
    """
    try:
        socket.setdefaulttimeout(3)
        socket.create_connection(("gnu.org", 80))
        printer.success("Internet Connection is Available..!")
    except OSError as sock_error:
        printer.warning(
            f"Internet Connection is Unavailable or some other problem occurred..!\n{sock_error}"
        )


VERSION = _get_git_ref()

# Pre-rendered ANSI banner passed to the TUI and fallback print paths.
_BANNER_LINES = (
    Fore.LIGHTBLACK_EX
    + """\
 ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·
██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.
██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄
██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█
▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀"""
    + Style.RESET_ALL
    + f"\nBuild {VERSION} / Vili (@vil) / https://vili.dev\n"
)


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------


def _display_help(
    menu_tools: tuple[BaseTool, ...], proxy_tool: BaseTool | None
) -> None:
    print(Fore.LIGHTCYAN_EX)
    print(
        f"H4X-Tools build: {VERSION} - A modular, terminal-based toolkit for OSINT, "
        "reconnaissance, and scraping - built in Python, runs on Linux and Windows."
    )
    print("Repository link: https://github.com/vil/h4x-tools")
    print("\nMade in Finland, with love.\n")

    print("Available Tools:")
    print("------------------")
    for index, tool in enumerate(menu_tools, start=1):
        aliases = ", ".join(tool.aliases)
        print(f"* {str(index).zfill(2)}. {tool.name} ({aliases}) - {tool.description}")

    if proxy_tool is not None:
        print("\nGlobal Utilities:")
        print("------------------")
        aliases = ", ".join(proxy_tool.aliases)
        print(f"* P  {proxy_tool.name} ({aliases}) - {proxy_tool.description}")

    print("\nNavigation (TUI menu):")
    print("------------------")
    print("  ↑ / ↓       Move through the tool list")
    print("  Enter       Run the highlighted tool")
    print("  0–9         Type a number to jump directly, then Enter to confirm")
    print("  Backspace   Delete the last typed digit")
    print("  Esc         Clear typed digits, or quit if nothing is typed")
    print("  P           Open Proxy Manager")
    print("  ?           Show this help screen")
    print("  q           Quit")
    print("\n  Inside any tool prompt, arrow keys move the cursor, Home/End jump")
    print("  to line boundaries, and Ctrl-A / Ctrl-E work as expected.")

    print("\nAdding Tools:")
    print("------------------")
    print(
        "Create a Python file in tools/, subclass tools.base.BaseTool, set "
        "id/name/description/order/aliases/arguments, and implement run(). "
        "H4X-Tools discovers it automatically at startup."
    )

    print("\nClosing the Toolkit:")
    print("----------------------")
    print(
        "Press q or Esc in the menu, or use one of: " + ", ".join(sorted(QUIT_COMMANDS))
    )

    print("\nLicense and Credits:")
    print("---------------------")
    print(
        "H4X-Tools is under the GNU General Public License v3, made by Vili (@vil).\n"
        "This toolkit is for educational and authorised security research purposes only."
    )

    print(Style.RESET_ALL, end="")


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def _build_parser(all_tools: tuple[BaseTool, ...]) -> argparse.ArgumentParser:
    """
    Build the H4X-Tools command-line parser from discovered tool metadata.

    All tools — including non-menu ones like the Proxy Manager — get their
    CLI flags registered here so they remain reachable from the command line.

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
    for tool in all_tools:
        tool.add_cli_arguments(tool_group)

    return parser


def _cli_tool_selected(
    args: argparse.Namespace, all_tools: tuple[BaseTool, ...]
) -> bool:
    """
    Determine whether any direct-run tool flag was provided.

    :param args: Parsed CLI args.
    :param all_tools: All discovered tools (including non-menu tools).
    :return: ``True`` if at least one tool should run directly.
    """
    return any(tool.selected(args) for tool in all_tools)


def _run_cli_tools(args: argparse.Namespace, all_tools: tuple[BaseTool, ...]) -> None:
    """
    Execute tool flags directly and exit without opening the menu.

    Tools run in discovery order when multiple flags are provided.

    :param args: Parsed CLI args.
    :param all_tools: All discovered tools (including non-menu tools).
    """
    for tool in all_tools:
        if not tool.selected(args):
            continue

        try:
            printer.verbose(f"Running {tool.name}")
            tool.run_from_cli(args)
        except KeyboardInterrupt:
            printer.warning("Cancelled..!")
            break


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(args: argparse.Namespace | None = None) -> None:
    # discover_tools() returns ALL tools, including non-menu tools.
    all_tools = discover_tools()

    if args is None:
        args = _build_parser(all_tools).parse_args()

    printer.set_verbosity(verbose=args.verbose > 0, debug_enabled=args.debug)
    config.init_config()

    # Split into menu-visible tools and the special-access proxy manager.
    menu_tools = tuple(t for t in all_tools if t.menu_visible)
    proxy_tool: BaseTool | None = next(
        (t for t in all_tools if t.id == "proxy_manager"), None
    )

    if args.list_tools:
        _display_help(menu_tools, proxy_tool)
        return

    if not args.no_internet_check:
        _internet_check()
        time.sleep(0.5)

    printer.debug("DEBUG IS ON.")

    if _cli_tool_selected(args, all_tools):
        printer.set_pause_after_tool(False)
        _run_cli_tools(args, all_tools)
        return

    printer.set_pause_after_tool(True)
    menu_options = {str(index): tool for index, tool in enumerate(menu_tools, start=1)}

    while True:
        choice = tui.run_menu(menu_tools, _BANNER_LINES)

        if choice == "quit" or choice is None:
            printer.warning("Quitting... Goodbye!")
            print(Style.RESET_ALL)
            time.sleep(0.5)
            break

        if choice == "help":
            _display_help(menu_tools, proxy_tool)
            printer.user_input("Done reading? Press the Enter key.")
            continue

        if choice == "proxy":
            if proxy_tool is not None:
                try:
                    proxy_tool.run()
                except KeyboardInterrupt:
                    printer.warning("Cancelled..!")
            else:
                printer.warning("Proxy Manager is not available.")
            continue

        if choice in menu_options:
            try:
                menu_options[choice].run()
            except KeyboardInterrupt:
                printer.warning("Cancelled..!")
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
            sys.exit()
