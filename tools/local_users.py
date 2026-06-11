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
from tools.base import BaseTool


class LocalUsersTool(BaseTool):
    id = "local_users"
    name = "Local Users"
    order = 16
    aliases = ("--local-users",)
    description = "Enumerates all local user accounts on the system, with Linux and Windows-specific account details."

    def run(self) -> None:
        from utils import local_users

        printer.info("Scanning for local accounts...")
        local_users.scan_for_local_users()
