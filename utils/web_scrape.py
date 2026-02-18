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

import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from colorama import Style

from helper import printer, randomuser, timer


def _export_links(links: set, base_url: str, format_type: str = "txt") -> None:
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
        match format_type.lower():
            case "txt":
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
            case "csv":
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
            case "json":
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
            case _:
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
    printer.debug(f"Scraping {urlparse(url).netloc}")

    # Use a fresh set for every invocation so state never leaks between runs.
    scraped_links: set[str] = set()

    try:
        response = printer.user_input(
            "Do you want to scrape the linked pages as well? (y/N) : "
        )
        if response.lower() in {"y", "yes"}:
            printer.info(
                f"Scraping links from {Style.BRIGHT}{url}{Style.RESET_ALL} and all linked pages..."
            )
            printer.warning("This may take a while depending on the size of the site.")
            printer.noprefix("")
            printer.section("Scraped Links")
            asyncio.run(_scrape_links(url, scraped_links, recursive=True))
            printer.noprefix("")
            printer.success("Scraping completed.")
        else:
            printer.info(f"Scraping links from {Style.BRIGHT}{url}{Style.RESET_ALL}...")
            printer.noprefix("")
            printer.section("Scraped Links")
            asyncio.run(_scrape_links(url, scraped_links, recursive=False))
            printer.noprefix("")
            printer.success("Scraping completed.")

        # Ask user if they want to export the results
        if scraped_links:
            printer.info(f"{len(scraped_links)} link(s) collected in total.")
            export_response = printer.user_input(
                "Do you want to export the scraped links? (y/N) : "
            )
            if export_response.lower() in {"y", "yes"}:
                printer.noprefix("")
                printer.section("Export")
                printer.info("  1 : TXT  (plain text)")
                printer.info("  2 : CSV  (comma-separated values)")
                printer.info("  3 : JSON (structured data)")

                format_choice = printer.user_input(
                    "Choose format (1/2/3) [default: 1] : "
                ).strip()

                format_map = {
                    "1": "txt",
                    "2": "csv",
                    "3": "json",
                    "": "txt",  # default
                }

                export_format = format_map.get(format_choice, "txt")
                _export_links(scraped_links, url, export_format)

    except KeyboardInterrupt:
        printer.error("Cancelled..!")
    except Exception as e:
        printer.error(f"Error : {e}")


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetches the HTML content of a URL.

    :param session: The shared aiohttp client session.
    :param url: URL to fetch.
    :return: Response body as text, or an empty string on error.
    """
    headers = {"User-Agent": str(randomuser.GetUser())}
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except Exception:
        return ""


async def _parse_links(content: str, base_url: str) -> list[tuple[str, str]]:
    """
    Parses all anchor tags from *content* and returns absolute (href, text) pairs.

    :param content: Raw HTML string.
    :param base_url: Base URL used to resolve relative hrefs.
    :return: List of (absolute_url, link_text) tuples.
    """
    soup = BeautifulSoup(content, "html.parser")
    return [
        (urljoin(base_url, str(link.get("href"))), link.get_text(strip=True))
        for link in soup.find_all("a")
    ]


async def _scrape_links(
    url: str,
    scraped_links: set[str],
    recursive: bool = False,
) -> None:
    """
    Scrapes links from *url* and, optionally, from every discovered page.

    :param url: The URL to scrape.
    :param scraped_links: Shared set used to track already-visited URLs across
                          recursive calls, preventing infinite loops.
    :param recursive: When True, every newly discovered URL is scraped as well.
    """
    async with aiohttp.ClientSession() as session:
        html_content = await _fetch(session, url)
        links = await _parse_links(html_content, url)

        for href, text in links:
            if href not in scraped_links:
                scraped_links.add(href)
                printer.success(
                    f"{len(scraped_links)} Link(s) found : "
                    f"{Style.BRIGHT}{href} - {text}{Style.RESET_ALL}"
                )

                if recursive:
                    await _scrape_links(href, scraped_links, recursive=True)
