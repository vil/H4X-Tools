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


class EmailSearchTool(BaseTool):
    id = "email_search"
    name = "Email Search"
    order = 6
    aliases = ("--email", "--email-search")
    description = "Checks an email address against 100+ websites and services using holehe to identify where the address is registered."
    arguments = (ToolArgument("email", "EMAIL", "Run email search."),)

    def run(self, email: str | None = None) -> None:
        from utils import email_search

        printer.info(
            "holehe will check the address against 100+ websites and show where it is registered."
        )
        email = str(email or printer.user_input("Enter an email address : \t"))
        email_search.search(email=email)
