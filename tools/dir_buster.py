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


class DirBusterTool(BaseTool):
    id = "dir_buster"
    name = "Dir Buster"
    order = 14
    aliases = ("--dirbuster", "--dir-buster")
    description = "Asynchronously bruteforces directory and file paths on a target website using a built-in wordlist, printing every HTTP 200 URL."
    arguments = (ToolArgument("domain", "DOMAIN", "Run directory buster for DOMAIN."),)

    def run(self, domain: str | None = None) -> None:
        from utils import dirbuster

        domain = domain or printer.user_input("Enter a domain : \t")
        dirbuster.bust(domain=domain)
