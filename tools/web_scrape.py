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


class WebScrapeTool(BaseTool):
    id = "web_scrape"
    name = "Web Scrape"
    order = 11
    aliases = ("--webscrape", "--web-scrape")
    description = "Asynchronously harvests hyperlinks, phone numbers, and emails from a target URL, with optional recursive crawling and export."
    arguments = (ToolArgument("url", "URL", "Run web scrape for URL."),)

    def run(self, url: str | None = None) -> None:
        from utils import web_scrape

        url = str(url or printer.user_input("Enter a URL : \t"))
        web_scrape.scrape(url=url)
