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


class IgScrapeTool(BaseTool):
    id = "ig_scrape"
    name = "Ig Scrape"
    order = 1
    aliases = ("--igscrape", "--ig-scrape", "--instagram", "--ig")
    description = (
        "Two-track Instagram OSINT scraper. Guest mode uses the ensta Guest API for public profile data and recent posts. "
        "Authenticated mode can query Instagram's private mobile API for richer public account data. Results can be exported as TXT, CSV, or JSON."
    )
    arguments = (
        ToolArgument("target", "USERNAME", "Run Instagram scrape for USERNAME."),
    )

    def run(self, target: str | None = None) -> None:
        from utils import ig_scrape

        target = str(
            target or printer.user_input("Enter a target username : \t")
        ).replace(" ", "_")
        ig_scrape.scrape(target=target)
