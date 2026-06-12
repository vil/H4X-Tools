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
        "Authenticated mode can query Instagram's private mobile API for richer public account data. Results can be exported as TXT, CSV, or JSON. "
        "New CLI flags: --session-id, --skip-obf (true/false), --comments-limit N."
    )
    arguments = (
        ToolArgument("target", "USERNAME", "Run Instagram scrape for USERNAME."),
        ToolArgument(
            "session_id",
            "SESSION",
            "Instagram sessionid cookie value (optional). If provided, the tool will run in authenticated mode.",
            flags=("--session-id",),
            parser_type=str,
            default=None,
        ),
        ToolArgument(
            "skip_obf",
            "BOOL",
            "If 'true', skip the advanced recovery lookup for obfuscated contact info. Accepts true/false.",
            flags=("--skip-obf",),
            parser_type=str,
            default=None,
        ),
        ToolArgument(
            "comments_limit",
            "N",
            "Maximum comments to fetch per post (0 to skip). If omitted you'll be prompted when running interactively.",
            flags=("--comments-limit",),
            parser_type=int,
            default=None,
        ),
    )

    def run(
        self,
        target: str | None = None,
        session_id: str | None = None,
        skip_obf: str | None = None,
        comments_limit: int | None = None,
    ) -> None:
        from utils import ig_scrape

        target = str(
            target or printer.user_input("Enter a target username : \t")
        ).replace(" ", "_")

        # Build keyword args only for options the user supplied via CLI
        kwargs: dict[str, object] = {}
        if session_id:
            kwargs["session_id"] = session_id

        if skip_obf is not None:
            val = str(skip_obf).strip().lower()
            skip = val in {"1", "true", "yes", "y"}
            # fetch_obf is the inverse of skip_obf
            kwargs["fetch_obf"] = not skip

        if comments_limit is not None:
            # comments_limit is an int (parser_type=int), pass through
            kwargs["comments_limit"] = comments_limit

        ig_scrape.scrape(target=target, **kwargs)
