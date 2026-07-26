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

from helper import printer, proxymanager
from tools.base import BaseTool

QUIT_COMMANDS = {"quit", "exit", "q", "kill", "0"}

class ProxyManagerTool(BaseTool):
    id = "proxy_manager"
    name = "Proxy Manager"
    order = 99
    aliases = ("--proxy-manager", "--proxies")
    description = (
        "Configure HTTP/SOCKS proxies for H4X-Tools to route network traffic through, "
        "with optional round-robin rotation to avoid rate limiting."
    )
    # Accessed via the P shortcut in the TUI menu, not as a numbered entry.
    menu_visible = False

    # No CLI arguments - the tool always opens its interactive sub-menu.

    def run(self) -> None:
        self._menu()

    # ------------------------------------------------------------------
    # Interactive menu
    # ------------------------------------------------------------------

    def _menu(self) -> None:
        while True:
            proxies = proxymanager.list_proxies()
            enabled = proxymanager.is_enabled()
            rotating = proxymanager.is_rotating()

            printer.noprefix("")
            printer.section("Proxy Manager")
            printer.info(f"Status   : {'Enabled' if enabled else 'Disabled'}")
            printer.info(f"Rotation : {'On (round-robin)' if rotating else 'Off (first proxy only)'}")
            printer.info(f"Proxies  : {len(proxies)} configured")
            printer.noprefix("")
            printer.noprefix("[1] List proxies")
            printer.noprefix("[2] Add proxy")
            printer.noprefix("[3] Remove proxy")
            printer.noprefix("[4] Test all proxies")
            printer.noprefix("[5] Toggle proxy routing")
            printer.noprefix("[6] Toggle rotation")
            printer.noprefix("[7] Clear all proxies")
            printer.noprefix("[0] Back")
            printer.noprefix("")

            choice = printer.user_input("Choose an option : \t").strip()

            if choice == "1":
                self._list_proxies()
            elif choice == "2":
                self._add_proxy()
            elif choice == "3":
                self._remove_proxy()
            elif choice == "4":
                self._test_proxies()
            elif choice == "5":
                self._toggle_enabled(enabled)
            elif choice == "6":
                self._toggle_rotation(rotating)
            elif choice == "7":
                self._clear_proxies()
            elif choice in QUIT_COMMANDS:
                break
            else:
                printer.error("Invalid option.")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _list_proxies(self) -> None:
        proxies = proxymanager.list_proxies()
        printer.noprefix("")
        if not proxies:
            printer.warning("No proxies configured.")
            return
        printer.section("Configured Proxies")
        for i, proxy in enumerate(proxies):
            printer.success(f"[{i}] {proxy}")

    def _add_proxy(self) -> None:
        printer.noprefix("")
        printer.info("Supported proxy formats:")
        printer.noprefix("    http://host:port")
        printer.noprefix("    http://user:pass@host:port")
        printer.noprefix("    socks5://host:port")
        printer.noprefix("    socks5://user:pass@host:port")
        printer.noprefix("")
        url = printer.user_input("Proxy URL : \t").strip()
        if url:
            proxymanager.add_proxy(url)

    def _remove_proxy(self) -> None:
        proxies = proxymanager.list_proxies()
        if not proxies:
            printer.warning("No proxies to remove.")
            return
        self._list_proxies()
        printer.noprefix("")
        raw = printer.user_input("Index to remove : \t").strip()
        try:
            index = int(raw)
        except ValueError:
            printer.error("Enter a valid number.")
            return
        proxymanager.remove_proxy(index)

    def _test_proxies(self) -> None:
        printer.noprefix("")
        proxymanager.test_all_proxies()

    def _toggle_enabled(self, currently_enabled: bool) -> None:
        new_state = not currently_enabled
        proxymanager.set_enabled(new_state)
        printer.success(f"Proxy routing {'enabled' if new_state else 'disabled'}.")

    def _toggle_rotation(self, currently_rotating: bool) -> None:
        new_state = not currently_rotating
        proxymanager.set_rotating(new_state)
        printer.success(f"Proxy rotation turned {'on' if new_state else 'off'}.")

    def _clear_proxies(self) -> None:
        printer.noprefix("")
        confirm = printer.user_input("Remove ALL proxies? (y/N) : \t").strip().lower()
        if confirm == "y":
            proxymanager.clear_proxies()
        else:
            printer.info("Cancelled.")
