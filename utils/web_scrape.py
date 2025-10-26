"""
Copyright (c) 2023-2025. Vili and contributors.

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

import aiohttp
import asyncio
import json
import csv
from typing import Any
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from colorama import Style

from helper import printer, timer
from helper import randomuser

scraped_links = set()


def export_links(links: set, base_url: str, format_type: str = "txt") -> None:
    """
    Exports scraped links to a file in the specified format.

    :param links: Set of scraped links
    :param base_url: Base URL that was scraped
    :param format_type: Export format ('txt', 'csv', or 'json')
    """
    if not links:
        printer.warning("No links to export!")
        return

    # Create output directory if it doesn't exist
    output_dir = Path("scraped_data")
    output_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(base_url).netloc.replace(".", "_")
    filename = f"{domain}_{timestamp}"

    try:
        if format_type.lower() == "txt":
            filepath = output_dir / f"{filename}.txt"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Scraped links from: {base_url}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total links: {len(links)}\n")
                f.write("-" * 80 + "\n\n")
                for link in sorted(links):
                    f.write(f"{link}\n")
            printer.success(
                f"Links exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
            )

        elif format_type.lower() == "csv":
            filepath = output_dir / f"{filename}.csv"
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["URL", "Domain", "Path"])
                for link in sorted(links):
                    parsed = urlparse(link)
                    writer.writerow([link, parsed.netloc, parsed.path])
            printer.success(
                f"Links exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
            )

        elif format_type.lower() == "json":
            filepath = output_dir / f"{filename}.json"
            link_data = {
                "metadata": {
                    "source_url": base_url,
                    "scraped_date": datetime.now().isoformat(),
                    "total_links": len(links),
                },
                "links": [
                    {
                        "url": link,
                        "domain": urlparse(link).netloc,
                        "path": urlparse(link).path,
                        "scheme": urlparse(link).scheme,
                    }
                    for link in sorted(links)
                ],
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(link_data, f, indent=2, ensure_ascii=False)
            printer.success(
                f"Links exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
            )

        else:
            printer.error(
                f"Invalid format: {format_type}. Use 'txt', 'csv', or 'json'."
            )

    except Exception as e:
        printer.error(f"Error exporting links: {e}")


@timer.timer(require_input=True)
def scrape(url: str) -> None:
    """
    Scrapes links from the given url.

    :param url: url of the website.
    """
    base_url = urlparse(url).netloc
    printer.debug(f"Scraping {base_url}")

    try:
        response = printer.inp(
            "Do you want to scrape the linked pages as well? (y/N) : "
        )
        if response.lower() == "y" or response.lower() == "yes":
            printer.info(
                f"Trying to scrape links from {Style.BRIGHT}{url}{Style.RESET_ALL} and its linked pages as well..."
            )
            printer.warning(
                "This may take a while depending on the sizes of the sites."
            )

            asyncio.run(scrape_links(url, recursive=True))
            printer.success("Scraping linked pages completed..!")
        else:
            printer.info(
                f"Trying to scrape links from {Style.BRIGHT}{url}{Style.RESET_ALL}..."
            )
            asyncio.run(scrape_links(url, recursive=False))
            printer.success("Scraping completed..!")

        # Ask user if they want to export the results
        if scraped_links:
            export_response = printer.inp(
                "\nDo you want to export the scraped links? (y/N) : "
            )
            if export_response.lower() == "y" or export_response.lower() == "yes":
                printer.info("Available export formats:")
                printer.info("  1. TXT (plain text)")
                printer.info("  2. CSV (comma-separated values)")
                printer.info("  3. JSON (structured data)")

                format_choice = printer.inp(
                    "Choose format (1/2/3) [default: 1] : "
                ).strip()

                format_map = {
                    "1": "txt",
                    "2": "csv",
                    "3": "json",
                    "": "txt",  # default
                }

                export_format = format_map.get(format_choice, "txt")
                export_links(scraped_links, url, export_format)

            # Clear scraped links for next run
            scraped_links.clear()

    except Exception as e:
        printer.error(f"Error : {e}")
    except KeyboardInterrupt:
        printer.error("Cancelled..!")


async def fetch(session, url: str) -> str:
    headers = {"User-Agent": f"{randomuser.GetUser()}"}
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def parse_links(content, base_url: str) -> list[tuple[str | bytes | Any, str]]:
    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all("a")
    return [(urljoin(base_url, link.get("href")), link.text) for link in links]


async def scrape_links(url: str, recursive=False) -> None:
    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, url)
        links = await parse_links(html_content, url)

        for href, text in links:
            if href not in scraped_links:
                scraped_links.add(href)
                printer.success(
                    f"{len(scraped_links)} Link(s) found : {Style.BRIGHT}{href} - {text}{Style.RESET_ALL}"
                )

                if recursive:
                    # await asyncio.sleep(0.5)
                    await scrape_links(href)  # recursively scrape linked pages
