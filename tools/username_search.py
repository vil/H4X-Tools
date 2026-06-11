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

from helper import printer
from tools.base import BaseTool, ToolArgument


class UsernameSearchTool(BaseTool):
    id = "username_search"
    name = "Username Search"
    order = 5
    aliases = ("--username", "--username-search")
    description = (
        "Checks a username across a configurable number of websites using Maigret's maintained site database and detection engines. "
        "Results can optionally be exported as TXT, CSV, or JSON."
    )
    arguments = (ToolArgument("username", "USERNAME", "Run Maigret username search."),)

    def run(self, username: str | None = None) -> None:
        from utils import search_username

        printer.info(
            "Maigret will check the username with configurable scan options and optional TXT/CSV/JSON export."
        )
        username = str(
            username or printer.user_input("Enter a target username : \t")
        ).replace(" ", "_")
        search_username.search(username=username)
