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
import logging
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from colorama import Style

from helper import printer, proxymanager, timer

REPORT_DIR = Path("scraped_data/maigret")
MAIGRET_DB_PATH = Path.home() / ".maigret" / "data.json"
DEFAULT_SITE_COUNT = 500
DEFAULT_TIMEOUT = 30
DEFAULT_CONNECTIONS = 100
DEFAULT_RETRIES = 0
_USERNAME_RE = re.compile(r"^[A-Za-z0-9._@-]{1,128}$")


@dataclass
class MaigretConfig:
    """Runtime options for a Maigret username search."""

    site_count: int
    timeout: int = DEFAULT_TIMEOUT
    connections: int = DEFAULT_CONNECTIONS
    retries: int = DEFAULT_RETRIES
    print_errors: bool = False
    save_format: str | None = None


@timer.timer(require_input=True)
def search(username: str, site_count: int | None = None) -> None:
    """
    Searches for a username using Maigret's Python library API.

    Loads Maigret's bundled site database directly, runs the async search via
    ``asyncio.run``, and optionally exports a H4X-Tools report in TXT, CSV,
    or JSON format.

    Thanks to Maigret — https://github.com/soxoj/maigret

    :param username: The username to search for.
    :param site_count: Optional number of top-ranked Maigret sites to scan.
                       If omitted, the user is prompted interactively.
    """
    username = username.strip()

    if not _validate_username(username):
        return

    db = _load_db()
    if db is None:
        printer.error(
            "Could not load Maigret site database. "
            f"Make sure Maigret is installed: {Style.BRIGHT}pip install maigret{Style.RESET_ALL}"
        )
        return

    available_sites = len(db.sites)
    config = _ask_config(available_sites, site_count)
    if config is None:
        return

    printer.info(
        f"Searching for {Style.BRIGHT}{username}{Style.RESET_ALL} with Maigret "
        f"across the top {Style.BRIGHT}{config.site_count}{Style.RESET_ALL} sites..."
    )
    printer.info(
        f"Timeout: {Style.BRIGHT}{config.timeout}s{Style.RESET_ALL} | "
        f"Connections: {Style.BRIGHT}{config.connections}{Style.RESET_ALL} | "
        f"Retries: {Style.BRIGHT}{config.retries}{Style.RESET_ALL}"
    )
    printer.info("This can take a while depending on network conditions.")

    try:
        results = _run_maigret(username, config, db)
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return

    if results is None:
        return

    claimed = _print_summary(username, results)

    if config.save_format:
        _save_report(username, results, claimed, config)
    else:
        printer.info("Report saving skipped.")

    printer.info("Credits to Soxoj and contributors for Maigret.")


# Internal helpers


def _validate_username(username: str) -> bool:
    """
    Performs basic validation before handing the value to Maigret.

    Maigret supports many identifier types, but this wrapper is the normal
    username flow, so we keep input to common username characters that are also
    safe in report filenames across platforms.

    :param username: The username to validate.
    :return: ``True`` if it is safe to pass to Maigret, otherwise ``False``.
    """
    if not username:
        printer.error("Username cannot be empty.")
        return False

    if not _USERNAME_RE.match(username):
        printer.error(
            "Username can only contain letters, numbers, dots, underscores, hyphens, and @."
        )
        return False

    return True


def _load_db():
    """
    Loads the Maigret site database.

    Tries the database bundled with the installed Maigret package first, then
    falls back to the user-level copy at ``~/.maigret/data.json``.

    :return: A loaded ``MaigretDatabase`` instance, or ``None`` on failure.
    """
    try:
        from maigret.sites import MaigretDatabase
    except ImportError:
        return None

    # Prefer the copy bundled with the installed package so we always have a
    # database even before the user has run `maigret --update-db`.
    try:
        import maigret as _maigret_pkg

        bundled = Path(_maigret_pkg.__file__).parent / "resources" / "data.json"
        if bundled.exists():
            db = MaigretDatabase().load_from_path(str(bundled))
            printer.verbose(
                f"Loaded Maigret database: {Style.BRIGHT}{len(db.sites)}{Style.RESET_ALL} sites (bundled)."
            )
            return db
    except Exception as exc:
        printer.warning(f"Could not load bundled Maigret database: {exc}")

    # Fall back to the user-level database updated by `maigret --update-db`.
    if MAIGRET_DB_PATH.exists():
        try:
            db = MaigretDatabase().load_from_path(str(MAIGRET_DB_PATH))
            printer.verbose(
                f"Loaded Maigret database: {Style.BRIGHT}{len(db.sites)}{Style.RESET_ALL} sites "
                f"({Style.BRIGHT}{MAIGRET_DB_PATH}{Style.RESET_ALL})."
            )
            return db
        except Exception as exc:
            printer.warning(f"Could not load user Maigret database: {exc}")

    return None


def _ask_config(
    available_sites: int | None,
    preselected_site_count: int | None = None,
) -> MaigretConfig | None:
    """
    Prompts for Maigret runtime options.

    :param available_sites: Total available Maigret site count, if known.
    :param preselected_site_count: Optional site count passed by callers/tests.
    :return: Maigret configuration or ``None`` if cancelled.
    """
    if available_sites is not None:
        printer.info(
            f"Maigret has {Style.BRIGHT}{available_sites}{Style.RESET_ALL} sites available."
        )

    if preselected_site_count is None:
        site_count = _ask_site_count(available_sites)
    else:
        site_count = _normalize_site_count(preselected_site_count, available_sites)

    if site_count is None:
        return None

    printer.noprefix("")
    printer.section("Maigret Options")
    printer.info("Press Enter to keep each default value.")
    printer.info(
        "Tip: if Maigret reports many connecting failures or access-denied errors, "
        "try fewer connections, e.g. 10-25."
    )

    timeout = _ask_int(
        "Request timeout in seconds",
        default=DEFAULT_TIMEOUT,
        minimum=5,
        maximum=300,
    )
    if timeout is None:
        return None

    connections = _ask_int(
        "Parallel connections",
        default=DEFAULT_CONNECTIONS,
        minimum=1,
        maximum=500,
    )
    if connections is None:
        return None

    retries = _ask_int(
        "Retries for temporarily failed requests",
        default=DEFAULT_RETRIES,
        minimum=0,
        maximum=10,
    )
    if retries is None:
        return None

    print_errors = _ask_yes_no("Print detailed site errors?", default=False)
    if print_errors is None:
        return None

    save_format = _ask_save_report()

    return MaigretConfig(
        site_count=site_count,
        timeout=timeout,
        connections=connections,
        retries=retries,
        print_errors=print_errors,
        save_format=save_format,
    )


def _ask_site_count(available_sites: int | None) -> int | None:
    """
    Asks how many top-ranked Maigret sites to scan.

    Empty input keeps ``DEFAULT_SITE_COUNT``. If the local database count is
    known, values above that count are capped so Maigret is not asked to scan
    more sites than are available.

    :param available_sites: Total available Maigret site count, if known.
    :return: The selected site count, or ``None`` if the prompt is cancelled.
    """
    default_count = DEFAULT_SITE_COUNT
    if available_sites is not None:
        default_count = min(DEFAULT_SITE_COUNT, available_sites)

    max_text = f", max {available_sites}" if available_sites is not None else ""
    prompt = f"Number of sites to search (default {default_count}{max_text}) : \t"

    try:
        raw_value = printer.user_input(prompt).strip()
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return None

    if not raw_value:
        return default_count

    try:
        site_count = int(raw_value)
    except ValueError:
        printer.warning(
            f"Invalid site count. Using default of {Style.BRIGHT}{default_count}{Style.RESET_ALL}."
        )
        return default_count

    normalized = _normalize_site_count(site_count, available_sites)
    return normalized if normalized is not None else default_count


def _normalize_site_count(site_count: int, available_sites: int | None) -> int | None:
    """
    Validates and caps a requested Maigret site count.

    :param site_count: Requested number of sites to scan.
    :param available_sites: Total available Maigret site count, if known.
    :return: A safe site count, or ``None`` if invalid.
    """
    if site_count < 1:
        printer.warning(
            f"Site count must be at least 1. Using default of {Style.BRIGHT}{DEFAULT_SITE_COUNT}{Style.RESET_ALL}."
        )
        return (
            min(DEFAULT_SITE_COUNT, available_sites)
            if available_sites
            else DEFAULT_SITE_COUNT
        )

    if available_sites is not None and site_count > available_sites:
        printer.warning(
            f"Only {Style.BRIGHT}{available_sites}{Style.RESET_ALL} sites are available. "
            "Using that instead."
        )
        return available_sites

    return site_count


def _ask_int(
    label: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int | None:
    """
    Prompts for an integer option with bounds and a default.

    :param label: Human-readable option label.
    :param default: Value used for empty or invalid input.
    :param minimum: Minimum accepted value.
    :param maximum: Maximum accepted value.
    :return: Selected integer, or ``None`` if cancelled.
    """
    try:
        raw_value = printer.user_input(
            f"{label} ({minimum}-{maximum}, default {default}) : \t"
        ).strip()
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return None

    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        printer.warning(
            f"Invalid value for {label.lower()}. Using default of {Style.BRIGHT}{default}{Style.RESET_ALL}."
        )
        return default

    if value < minimum:
        printer.warning(
            f"{label} must be at least {minimum}. Using {Style.BRIGHT}{minimum}{Style.RESET_ALL}."
        )
        return minimum

    if value > maximum:
        printer.warning(
            f"{label} cannot exceed {maximum}. Using {Style.BRIGHT}{maximum}{Style.RESET_ALL}."
        )
        return maximum

    return value


def _ask_yes_no(label: str, *, default: bool = False) -> bool | None:
    """
    Prompts for a yes/no option.

    :param label: Human-readable option label.
    :param default: Default boolean used for empty input.
    :return: ``True``/``False`` or ``None`` if cancelled.
    """
    suffix = "Y/n" if default else "y/N"

    try:
        raw_value = printer.user_input(f"{label} ({suffix}) : ").strip().lower()
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return None

    if not raw_value:
        return default

    if raw_value in {"y", "yes"}:
        return True

    if raw_value in {"n", "no"}:
        return False

    printer.warning("Invalid choice. Using default.")
    return default


def _ask_save_report() -> str | None:
    """
    Ask whether to save a Maigret report and, if so, in which format.

    :return: ``'txt'``, ``'csv'``, or ``'json'`` if the user wants to save;
             ``None`` if they decline.
    """
    answer = printer.user_input("Save report to file? (y/N) : ").strip().lower()
    if answer not in {"y", "yes"}:
        return None

    printer.noprefix("")
    printer.section("Report Format")
    printer.info("  1 : TXT  (plain text report)")
    printer.info("  2 : CSV  (spreadsheet-friendly)")
    printer.info("  3 : JSON (full structured data)")

    format_map = {"1": "txt", "2": "csv", "3": "json", "": "txt"}
    choice = printer.user_input("Choose format (1/2/3) [default: 1] : ").strip()
    return format_map.get(choice, "txt")


def _run_maigret(username: str, config: MaigretConfig, db) -> dict[str, Any] | None:
    """
    Runs the Maigret search using the library API and returns raw results.

    Uses ``asyncio.run`` to drive the async ``maigret.search`` coroutine.
    A ``Notifier`` is attached so found accounts are printed live as Maigret
    discovers them. Progress bars are suppressed to keep H4X-Tools' UI clean.

    :param username: The validated username to search.
    :param config: Maigret runtime configuration.
    :param db: Loaded ``MaigretDatabase`` instance.
    :return: Raw Maigret results dict, or ``None`` on failure.
    """
    try:
        from maigret import Notifier
        from maigret import search as maigret_search
    except ImportError:
        printer.error(
            f"{Style.BRIGHT}maigret{Style.RESET_ALL} is not installed. "
            f"Install it with: {Style.BRIGHT}pip install maigret{Style.RESET_ALL}"
        )
        return None

    sites = db.ranked_sites_dict(top=config.site_count)

    # Gate Maigret's internal Python logging on H4X-Tools' verbosity level so
    # its WARNING-level messages don't leak through the root logger by default.
    logger = logging.getLogger("maigret")
    logger.setLevel(
        logging.DEBUG
        if printer.is_debug()
        else logging.WARNING
        if printer.is_verbose()
        else logging.ERROR
    )

    # QueryNotifyPrint prints each found account to the terminal in real time.
    notifier = Notifier(
        print_found_only=True,
        color=True,
        skip_check_errors=not config.print_errors,
    )

    proxy = proxymanager.get_proxy() or None

    try:
        results = asyncio.run(
            maigret_search(
                username=username,
                site_dict=sites,
                logger=logger,
                query_notify=notifier,
                proxy=proxy,
                timeout=config.timeout,
                is_parsing_enabled=True,
                no_progressbar=True,
                max_connections=config.connections,
                retries=config.retries,
            )
        )
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        printer.error(f"Maigret search failed: {exc}")
        return None

    return results


def _print_summary(username: str, results: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Prints a concise H4X-Tools summary from Maigret's result dict.

    Also displays any profile fields extracted via ``is_parsing_enabled``
    (bio, linked accounts, UIDs, etc.) grouped under each found site.

    :param username: The searched username.
    :param results: Raw results dict returned by ``maigret.search``.
    :return: Claimed account entries extracted from the results.
    """
    claimed = _claimed_accounts(results)

    printer.noprefix("")
    printer.section("Maigret Summary")

    if claimed:
        printer.success(
            f"Found {Style.BRIGHT}{len(claimed)}{Style.RESET_ALL} account(s) "
            f"for {Style.BRIGHT}{username}{Style.RESET_ALL}."
        )
        for account in claimed:
            ids = account.get("ids_data") or {}
            if ids:
                printer.info(
                    f"{Style.BRIGHT}{account['site']}{Style.RESET_ALL} — profile data:"
                )
                for key, value in ids.items():
                    if value:
                        printer.noprefix(f"    {key}: {value}")
    else:
        printer.warning(f"No claimed accounts found for {username}.")

    return claimed


def _save_report(
    username: str,
    results: dict[str, Any],
    claimed: list[dict[str, Any]],
    config: MaigretConfig,
) -> None:
    """
    Exports Maigret results to ``scraped_data/maigret/``.

    :param username: The searched username.
    :param results: Raw results dict returned by ``maigret.search``.
    :param claimed: Claimed accounts extracted from the results.
    :param config: Maigret runtime configuration used for the scan.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(username)
    fmt = config.save_format or "txt"

    try:
        match fmt.lower():
            case "txt":
                filepath = REPORT_DIR / f"maigret_{slug}_{timestamp}.txt"
                with filepath.open("w", encoding="utf-8") as fh:
                    fh.write("Maigret Username Search Report\n")
                    fh.write(f"Target      : {username}\n")
                    fh.write(
                        f"Date        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    fh.write(f"Sites       : {config.site_count}\n")
                    fh.write(f"Timeout     : {config.timeout}s\n")
                    fh.write(f"Connections : {config.connections}\n")
                    fh.write(f"Retries     : {config.retries}\n")
                    fh.write(f"Found       : {len(claimed)}\n")
                    fh.write("=" * 80 + "\n\n")

                    if claimed:
                        for account in claimed:
                            fh.write(f"Site : {account['site']}\n")
                            fh.write(f"URL  : {account['url'] or 'N/A'}\n")
                            fh.write(f"Rank : {account['rank']}\n")
                            tags = account.get("tags") or []
                            if tags:
                                fh.write(f"Tags : {', '.join(tags)}\n")
                            ids = account.get("ids_data") or {}
                            if ids:
                                fh.write("Profile data:\n")
                                for key, value in ids.items():
                                    if value:
                                        fh.write(f"  {key}: {value}\n")
                            fh.write("\n")
                    else:
                        fh.write("No claimed accounts found.\n")

                printer.success(
                    f"Report saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "csv":
                filepath = REPORT_DIR / f"maigret_{slug}_{timestamp}.csv"
                with filepath.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(
                        [
                            "username",
                            "site",
                            "url",
                            "rank",
                            "http_status",
                            "tags",
                        ]
                    )
                    for account in claimed:
                        writer.writerow(
                            [
                                username,
                                account["site"],
                                account["url"],
                                account["rank"],
                                account.get("http_status", ""),
                                ", ".join(account.get("tags") or []),
                            ]
                        )

                printer.success(
                    f"Report saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "json":
                filepath = REPORT_DIR / f"maigret_{slug}_{timestamp}.json"
                payload = {
                    "tool": "Maigret",
                    "target": username,
                    "timestamp": datetime.now().isoformat(),
                    "config": asdict(config),
                    "total_found": len(claimed),
                    "claimed_accounts": claimed,
                }
                with filepath.open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)

                printer.success(
                    f"Report saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case _:
                printer.error(f"Unknown format '{fmt}'. Use 'txt', 'csv', or 'json'.")

    except OSError as exc:
        printer.error(f"Could not write report file: {exc}")


def _slugify(value: str) -> str:
    """
    Converts a target value into a filesystem-safe slug.

    :param value: Raw target value.
    :return: Safe filename component.
    """
    return "".join(c if c.isalnum() or c in "-_.@" else "_" for c in value)[:80]


def _claimed_accounts(results: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extracts claimed accounts from Maigret's raw result dict.

    Each value in the results dict contains a ``"status"`` key that holds a
    ``MaigretCheckResult`` object. ``is_found()`` returns ``True`` when the
    status is ``CLAIMED``.

    :param results: Raw results dict returned by ``maigret.search``.
    :return: Claimed account entries sorted by Maigret rank and site name.
    """
    claimed: list[dict[str, Any]] = []

    for site_name, result in results.items():
        if not isinstance(result, dict):
            continue

        status = result.get("status")
        if status is None or not status.is_found():
            continue

        claimed.append(
            {
                "site": getattr(status, "site_name", None) or site_name,
                "url": getattr(status, "site_url_user", None)
                or result.get("url_user", ""),
                "rank": result.get("rank", sys.maxsize),
                "http_status": result.get("http_status"),
                "tags": list(getattr(status, "tags", None) or []),
                "ids_data": dict(getattr(status, "ids_data", None) or {}),
            }
        )

    claimed.sort(key=lambda item: (item["rank"], str(item["site"]).lower()))
    return claimed
