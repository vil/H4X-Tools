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

from tools.base import BaseTool


class WebReconnaissanceTool(BaseTool):
    id = "web_reconnaissance"
    name = "Web Reconnaissance"
    order = 2
    aliases = ("--webrecon", "--web-recon", "--web-reconnaissance")
    description = (
        "Multi-mode OSINT search powered by ddgs. Supports general, person, email, domain, username, phone number, "
        "and custom dork searches with optional TXT, CSV, or JSON export."
    )

    def run(self) -> None:
        from utils import web_reconnaissance

        web_reconnaissance.websearch()
