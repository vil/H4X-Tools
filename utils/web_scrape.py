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
import re
from collections import deque
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse

import aiohttp
from bs4 import BeautifulSoup
from colorama import Style

from helper import printer, randomuser, timer

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15, connect=5, sock_read=10)
MAX_CONCURRENT_REQUESTS = 12
MAX_CRAWL_PAGES = 250
EMAIL_REGEX = re.compile(
    r"\b[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+\b"
)
PHONE_REGEX = re.compile(
    r"(?<!\w)(?:\+|00)?\d{1,3}?[\s.\-/]?(?:\(?\d{2,4}\)?[\s.\-/]?){2,5}\d{2,4}(?!\w)"
)
DATE_LIKE_REGEX = re.compile(
    r"(?:\b\d{1,2}[./-](?:19|20)\d{2}\b|\b(?:19|20)\d{2}[./-]\d{1,2}\b)"
)
TIME_LIKE_REGEX = re.compile(r"\b\d{1,2}[.:]\d{2}(?:[.:]\d{2})?\b")
SKIPPED_EXTENSIONS = {
    ".7z",
    ".avi",
    ".bmp",
    ".css",
    ".csv",
    ".doc",
    ".docx",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".m4a",
    ".m4v",
    ".mov",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".rar",
    ".svg",
    ".tar",
    ".tgz",
    ".webp",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}


def _export_results(
    links: set[str],
    emails: set[str],
    phone_numbers: set[str],
    base_url: str,
    format_type: str = "txt",
) -> None:
    """
    Exports scraped links, emails and phone numbers to a file.

    :param links: Set of scraped links.
    :param emails: Set of scraped email addresses.
    :param phone_numbers: Set of scraped phone numbers.
    :param base_url: Base URL that was scraped.
    :param format_type: Export format ('txt', 'csv', or 'json').
    """
    if not links and not emails and not phone_numbers:
        printer.warning("No scraped data to export!")
        return

    output_dir = Path("scraped_data")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(base_url).netloc.replace(".", "_") or "scrape"
    filename = f"{domain}_{timestamp}"

    try:
        match format_type.lower():
            case "txt":
                filepath = output_dir / f"{filename}.txt"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Scraped data from: {base_url}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total links: {len(links)}\n")
                    f.write(f"Total emails: {len(emails)}\n")
                    f.write(f"Total phone numbers: {len(phone_numbers)}\n")
                    f.write("-" * 80 + "\n\n")

                    f.write("Links:\n")
                    for link in sorted(links):
                        f.write(f"{link}\n")

                    f.write("\nEmails:\n")
                    for email in sorted(emails):
                        f.write(f"{email}\n")

                    f.write("\nPhone numbers:\n")
                    for phone_number in sorted(phone_numbers):
                        f.write(f"{phone_number}\n")

                printer.success(
                    f"Scraped data exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )
            case "csv":
                filepath = output_dir / f"{filename}.csv"
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Type", "Value", "Domain", "Path"])

                    for link in sorted(links):
                        parsed = urlparse(link)
                        writer.writerow(["link", link, parsed.netloc, parsed.path])
                    for email in sorted(emails):
                        writer.writerow(["email", email, "", ""])
                    for phone_number in sorted(phone_numbers):
                        writer.writerow(["phone", phone_number, "", ""])

                printer.success(
                    f"Scraped data exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )
            case "json":
                filepath = output_dir / f"{filename}.json"
                data = {
                    "metadata": {
                        "source_url": base_url,
                        "scraped_date": datetime.now().isoformat(),
                        "total_links": len(links),
                        "total_emails": len(emails),
                        "total_phone_numbers": len(phone_numbers),
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
                    "emails": sorted(emails),
                    "phone_numbers": sorted(phone_numbers),
                }
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                printer.success(
                    f"Scraped data exported to {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )
            case _:
                printer.error(
                    f"Invalid format: {format_type}. Use 'txt', 'csv', or 'json'."
                )

    except Exception as e:
        printer.error(f"Error exporting scraped data: {e}")


@timer.timer(require_input=True)
def scrape(url: str) -> None:
    """
    Scrapes links, email addresses and phone numbers from the given url.

    :param url: url of the website.
    """
    url = _normalize_url(url) or url
    printer.debug(f"Scraping {urlparse(url).netloc or url}")

    scraped_links: set[str] = set()
    scraped_emails: set[str] = set()
    scraped_phone_numbers: set[str] = set()

    try:
        response = printer.user_input(
            "Do you want to scrape the linked pages as well? (y/N) : "
        )
        recursive = response.lower() in {"y", "yes"}
        max_crawl_pages = MAX_CRAWL_PAGES

        if recursive:
            max_crawl_pages = _ask_max_crawl_pages()
            printer.info(
                f"Scraping data from {Style.BRIGHT}{url}{Style.RESET_ALL} first, then linked pages..."
            )
            printer.warning(
                f"This may take a while. Crawl limit: {max_crawl_pages} pages, "
                f"concurrency: {MAX_CONCURRENT_REQUESTS}."
            )
        else:
            printer.info(f"Scraping data from {Style.BRIGHT}{url}{Style.RESET_ALL}...")

        printer.noprefix("")
        printer.section("Scraped Data")
        asyncio.run(
            _scrape_links(
                url,
                scraped_links,
                scraped_emails,
                scraped_phone_numbers,
                recursive=recursive,
                max_crawl_pages=max_crawl_pages,
            )
        )
        printer.noprefix("")
        printer.success("Scraping completed.")

        if scraped_links or scraped_emails or scraped_phone_numbers:
            printer.info(
                f"Collected {len(scraped_links)} link(s), "
                f"{len(scraped_emails)} email(s), "
                f"and {len(scraped_phone_numbers)} phone number(s) in total."
            )
            export_response = printer.user_input(
                "Do you want to export the scraped data? (y/N) : "
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
                    "": "txt",
                }

                export_format = format_map.get(format_choice, "txt")
                _export_results(
                    scraped_links,
                    scraped_emails,
                    scraped_phone_numbers,
                    url,
                    export_format,
                )

    except KeyboardInterrupt:
        printer.error("Cancelled..!")
    except Exception as e:
        printer.error(f"Error : {e}")


def _ask_max_crawl_pages() -> int:
    """
    Asks the user how many pages should be crawled when recursive scraping is enabled.
    """
    response = printer.user_input(
        f"Max pages to crawl [default: {MAX_CRAWL_PAGES}] : "
    ).strip()

    if not response:
        return MAX_CRAWL_PAGES

    try:
        max_pages = int(response)
    except ValueError:
        printer.warning(
            f"Invalid crawl limit. Using default of {MAX_CRAWL_PAGES} pages."
        )
        return MAX_CRAWL_PAGES

    if max_pages < 1:
        printer.warning(
            f"Crawl limit must be at least 1. Using default of {MAX_CRAWL_PAGES} pages."
        )
        return MAX_CRAWL_PAGES

    return max_pages


def _normalize_url(url: str) -> str | None:
    """
    Normalizes a URL for deduplication and crawling.
    """
    url = url.strip()
    if not url:
        return None

    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    path = parsed.path or "/"
    if any(path.lower().endswith(extension) for extension in SKIPPED_EXTENSIONS):
        return None

    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            parsed.query,
            "",
        )
    )


def _is_supported_content_type(content_type: str) -> bool:
    return not content_type or any(
        content_type.lower().startswith(supported_type)
        for supported_type in ("text/html", "application/xhtml+xml", "text/plain")
    )


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetches text content from a URL.

    :param session: The shared aiohttp client session.
    :param url: URL to fetch.
    :return: Response body as text, or an empty string on error.
    """
    try:
        async with session.get(url, allow_redirects=True) as response:
            if response.status >= 400:
                return ""

            content_type = response.headers.get("Content-Type", "")
            if not _is_supported_content_type(content_type):
                return ""

            return await response.text(errors="ignore")
    except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError):
        return ""


def _parse_page(
    content: str, base_url: str
) -> tuple[list[tuple[str, str]], set[str], set[str]]:
    """
    Parses links, emails and phone numbers from *content*.

    :param content: Raw HTML/text string.
    :param base_url: Base URL used to resolve relative hrefs.
    :return: Tuple of links, emails and phone numbers.
    """
    soup = BeautifulSoup(content, "html.parser")

    for tag in soup(("script", "style", "noscript")):
        tag.decompose()

    links: list[tuple[str, str]] = []
    emails: set[str] = set()
    phone_numbers: set[str] = set()

    for link in soup.find_all("a"):
        href_value = link.get("href")
        if not isinstance(href_value, str):
            continue

        href = href_value.strip()
        if not href:
            continue

        parsed_href = urlparse(href)
        if parsed_href.scheme == "mailto":
            email = unquote(parsed_href.path).split("?", 1)[0].strip().lower()
            if EMAIL_REGEX.fullmatch(email):
                emails.add(email)
            continue
        if parsed_href.scheme == "tel":
            phone_number = _clean_phone_number(unquote(parsed_href.path))
            if phone_number:
                phone_numbers.add(phone_number)
            continue

        absolute_url = _normalize_url(urljoin(base_url, href))
        if absolute_url:
            links.append((absolute_url, link.get_text(" ", strip=True)))

    text = soup.get_text(" ", strip=True)
    emails.update(email.lower() for email in EMAIL_REGEX.findall(text))

    for phone_match in PHONE_REGEX.findall(text):
        phone_number = _clean_phone_number(phone_match)
        if phone_number:
            phone_numbers.add(phone_number)

    return links, emails, phone_numbers


def _clean_phone_number(phone_number: str) -> str | None:
    phone_number = re.sub(r"\s+", " ", phone_number).strip(" .,/;-")
    digit_count = sum(character.isdigit() for character in phone_number)

    if not 7 <= digit_count <= 15:
        return None

    if _looks_like_date_or_time(phone_number):
        return None

    return phone_number


def _looks_like_date_or_time(value: str) -> bool:
    """
    Reject common date/time fragments that can look phone-like after regex matching.
    """
    if DATE_LIKE_REGEX.search(value):
        return True

    if TIME_LIKE_REGEX.search(value):
        return True

    groups = re.findall(r"\d+", value)
    if any(group.startswith(("19", "20")) and len(group) == 4 for group in groups):
        separator_count = sum(value.count(separator) for separator in (".", "/", "-"))
        if separator_count:
            return True

    return False


def _print_link(links: set[str], href: str, text: str) -> None:
    links.add(href)
    label = f" - {text}" if text else ""
    printer.success(
        f"{len(links)} Link(s) found : {Style.BRIGHT}{href}{label}{Style.RESET_ALL}"
    )


def _print_email(emails: set[str], email: str) -> None:
    emails.add(email)
    printer.success(
        f"{len(emails)} Email(s) found : {Style.BRIGHT}{email}{Style.RESET_ALL}"
    )


def _print_phone_number(phone_numbers: set[str], phone_number: str) -> None:
    phone_numbers.add(phone_number)
    printer.success(
        f"{len(phone_numbers)} Phone number(s) found : "
        f"{Style.BRIGHT}{phone_number}{Style.RESET_ALL}"
    )


async def _scrape_page(
    session: aiohttp.ClientSession,
    url: str,
) -> tuple[str, list[tuple[str, str]], set[str], set[str]]:
    html_content = await _fetch(session, url)
    if not html_content:
        return url, [], set(), set()

    links, emails, phone_numbers = _parse_page(html_content, url)
    return url, links, emails, phone_numbers


def _store_page_results(
    links: list[tuple[str, str]],
    emails: set[str],
    phone_numbers: set[str],
    scraped_links: set[str],
    scraped_emails: set[str],
    scraped_phone_numbers: set[str],
) -> list[str]:
    new_links: list[str] = []

    for href, text in links:
        if href not in scraped_links:
            _print_link(scraped_links, href, text)
            new_links.append(href)

    for email in emails:
        if email not in scraped_emails:
            _print_email(scraped_emails, email)

    for phone_number in phone_numbers:
        if phone_number not in scraped_phone_numbers:
            _print_phone_number(scraped_phone_numbers, phone_number)

    return new_links


async def _scrape_links(
    url: str,
    scraped_links: set[str],
    scraped_emails: set[str],
    scraped_phone_numbers: set[str],
    recursive: bool = False,
    max_crawl_pages: int = MAX_CRAWL_PAGES,
) -> None:
    """
    Scrapes links, email addresses and phone numbers from *url* and, optionally,
    from discovered pages. The target URL is always fetched and parsed before any
    discovered page is crawled.

    :param url: The URL to scrape.
    :param scraped_links: Shared set of discovered links.
    :param scraped_emails: Shared set of discovered email addresses.
    :param scraped_phone_numbers: Shared set of discovered phone numbers.
    :param recursive: When True, newly discovered URLs are crawled too.
    :param max_crawl_pages: Maximum number of pages to fetch, including the target URL.
    """
    normalized_url = _normalize_url(url)
    if not normalized_url:
        printer.warning(f"Invalid URL skipped: {url}")
        return

    headers = {"User-Agent": str(randomuser.GetUser())}
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, ttl_dns_cache=300)

    async with aiohttp.ClientSession(
        connector=connector,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    ) as session:
        visited = {normalized_url}

        _, links, emails, phone_numbers = await _scrape_page(session, normalized_url)
        pending_urls = deque(
            _store_page_results(
                links,
                emails,
                phone_numbers,
                scraped_links,
                scraped_emails,
                scraped_phone_numbers,
            )
        )

        if not recursive:
            return

        while pending_urls and len(visited) < max_crawl_pages:
            batch: list[str] = []
            while (
                pending_urls
                and len(batch) < MAX_CONCURRENT_REQUESTS
                and len(visited) < max_crawl_pages
            ):
                next_url = pending_urls.popleft()
                if next_url in visited:
                    continue
                visited.add(next_url)
                batch.append(next_url)

            if not batch:
                continue

            results = await asyncio.gather(
                *(_scrape_page(session, next_url) for next_url in batch)
            )

            for _, page_links, page_emails, page_phone_numbers in results:
                for discovered_url in _store_page_results(
                    page_links,
                    page_emails,
                    page_phone_numbers,
                    scraped_links,
                    scraped_emails,
                    scraped_phone_numbers,
                ):
                    if discovered_url not in visited:
                        pending_urls.append(discovered_url)

        if pending_urls and len(visited) >= max_crawl_pages:
            printer.warning(
                f"Stopped after reaching the crawl limit of {max_crawl_pages} pages."
            )
