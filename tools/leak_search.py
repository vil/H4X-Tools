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


class LeakSearchTool(BaseTool):
    id = "leak_search"
    name = "Leak Search"
    order = 7
    aliases = ("--leak", "--leak-search")
    description = (
        "Multi-source breach and credential intelligence for an email address, domain, or username. Queries stealer-log records "
        "and can cross-reference public leaked credential datasets with optional export."
    )
    arguments = (
        ToolArgument(
            "target", "TARGET", "Run leak search for an email, domain, or username."
        ),
    )

    def run(self, target: str | None = None) -> None:
        from utils import leak_search

        target = target or printer.user_input(
            "Enter a target (email/domain/username) : \t"
        )
        leak_search.lookup(target=target)
