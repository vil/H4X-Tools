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

import csv
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from colorama import Style

from helper import printer, timer

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
    Searches for a username using Maigret.

    H4X-Tools intentionally acts as a wrapper around Maigret here: it invokes
    Maigret's maintained site database/check engines, prints Maigret's results,
    and optionally exports a H4X-Tools report in TXT, CSV, or JSON format.

    Thanks to Maigret — https://github.com/soxoj/maigret

    :param username: The username to search for.
    :param site_count: Optional number of top-ranked Maigret sites to scan.
                       If omitted, the user is prompted interactively.
    """
    username = username.strip()

    if not _validate_username(username):
        return

    available_sites = _get_available_site_count()
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
        report = _run_maigret(username, config)
    except KeyboardInterrupt:
        printer.error("Cancelled..!")
        return

    if report is None:
        return

    claimed = _print_summary(username, report)

    if config.save_format:
        _save_report(username, report, claimed, config)
    else:
        printer.info("Report saving skipped.")

    printer.info("Credits to soxoj and contributors for Maigret.")


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


def _get_available_site_count() -> int | None:
    """
    Counts the sites available in Maigret's local database.

    Maigret stores the local database at ``~/.maigret/data.json``. The current
    format keeps sites under the top-level ``sites`` key, but this stays
    defensive in case the structure changes.

    :return: Number of available Maigret sites, or ``None`` if unavailable.
    """
    try:
        database = json.loads(MAIGRET_DB_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        printer.warning(
            f"Maigret database not found at {Style.BRIGHT}{MAIGRET_DB_PATH}{Style.RESET_ALL}. "
            f"Using default of {Style.BRIGHT}{DEFAULT_SITE_COUNT}{Style.RESET_ALL} sites."
        )
        return None
    except json.JSONDecodeError as exc:
        printer.warning(
            f"Could not parse Maigret database ({exc}). "
            f"Using default of {Style.BRIGHT}{DEFAULT_SITE_COUNT}{Style.RESET_ALL} sites."
        )
        return None
    except OSError as exc:
        printer.warning(
            f"Could not read Maigret database ({exc}). "
            f"Using default of {Style.BRIGHT}{DEFAULT_SITE_COUNT}{Style.RESET_ALL} sites."
        )
        return None

    sites = database.get("sites") if isinstance(database, dict) else None

    if isinstance(sites, dict | list):
        return len(sites)

    if isinstance(database, dict):
        return len(database)

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


def _run_maigret(username: str, config: MaigretConfig) -> dict[str, Any] | None:
    """
    Invokes Maigret and returns the parsed simple JSON report.

    H4X-Tools creates Maigret's JSON report in a temporary directory so it can
    summarize results without forcing the user to save anything. If the user
    opted to save a report, H4X-Tools exports the parsed results afterwards.

    :param username: The validated username to search.
    :param config: Maigret runtime configuration.
    :return: Parsed Maigret report, or ``None`` on failure.
    """
    with tempfile.TemporaryDirectory(prefix="h4x_maigret_") as temp_dir:
        temp_path = Path(temp_dir)
        report_path = _maigret_json_path(temp_path, username)

        command = [
            sys.executable,
            "-m",
            "maigret",
            username,
            "--top-sites",
            str(config.site_count),
            "--timeout",
            str(config.timeout),
            "--retries",
            str(config.retries),
            "--max-connections",
            str(config.connections),
            "--no-color",
            "--no-progressbar",
            "--json",
            "simple",
            "--folderoutput",
            str(temp_path),
        ]

        if config.print_errors:
            command.append("--print-errors")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=900,
            )
        except FileNotFoundError:
            printer.error(
                f"{Style.BRIGHT}maigret{Style.RESET_ALL} was not found. "
                f"Install it with: {Style.BRIGHT}pip install maigret{Style.RESET_ALL}"
            )
            return None
        except subprocess.TimeoutExpired:
            printer.error(
                "Maigret timed out after 15 minutes. "
                "Try again with fewer sites or fewer parallel connections."
            )
            return None
        except Exception as exc:
            printer.error(f"Unexpected error while running Maigret: {exc}")
            return None

        _print_maigret_output(result.stdout + result.stderr)

        if result.returncode != 0:
            printer.error(f"Maigret exited with status code {result.returncode}.")
            return None

        if not report_path.exists():
            printer.warning(
                "Maigret finished but did not create the internal JSON report."
            )
            return None

        return _load_report(report_path)


def _print_maigret_output(output: str) -> None:
    """
    Prints Maigret output while hiding the temporary internal JSON path.

    :param output: Combined stdout/stderr from Maigret.
    """
    for line in output.splitlines():
        clean = line.strip()
        if not clean:
            continue

        if "JSON simple report" in clean and "saved in" in clean:
            continue

        printer.noprefix(clean)


def _maigret_json_path(output_dir: Path, username: str) -> Path:
    """
    Builds Maigret's simple JSON report path for a username.

    :param output_dir: Directory passed to Maigret's ``--folderoutput`` flag.
    :param username: The username used by Maigret.
    :return: The expected JSON report path.
    """
    return output_dir / f"report_{username}_simple.json"


def _load_report(report_path: Path) -> dict[str, Any] | None:
    """
    Loads a Maigret JSON report.

    :param report_path: Path to Maigret's simple JSON report.
    :return: Parsed report, or ``None`` on failure.
    """
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        printer.error(f"Could not parse Maigret JSON report: {exc}")
        return None
    except OSError as exc:
        printer.error(f"Could not read Maigret JSON report: {exc}")
        return None

    if not isinstance(report, dict):
        printer.error("Maigret JSON report had an unexpected structure.")
        return None

    return report


def _print_summary(username: str, report: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Prints a concise H4X-Tools summary from Maigret's simple JSON report.

    :param username: The searched username.
    :param report: Parsed Maigret report.
    :return: Claimed account entries extracted from the report.
    """
    claimed = _claimed_accounts(report)

    printer.noprefix("")
    printer.section("Maigret Summary")

    if claimed:
        printer.success(
            f"Found {Style.BRIGHT}{len(claimed)}{Style.RESET_ALL} account(s) "
            f"for {Style.BRIGHT}{username}{Style.RESET_ALL}."
        )
    else:
        printer.warning(f"No claimed accounts found for {username}.")

    return claimed


def _save_report(
    username: str,
    report: dict[str, Any],
    claimed: list[dict[str, Any]],
    config: MaigretConfig,
) -> None:
    """
    Exports Maigret results to ``scraped_data/maigret/``.

    :param username: The searched username.
    :param report: Full parsed Maigret report.
    :param claimed: Claimed accounts extracted from the report.
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
                    "raw_report": report,
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


def _claimed_accounts(report: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extracts claimed accounts from Maigret's simple JSON report.

    :param report: Parsed Maigret report.
    :return: Claimed account entries sorted by Maigret rank and site name.
    """
    claimed: list[dict[str, Any]] = []

    for site_name, entry in report.items():
        if not isinstance(entry, dict):
            continue

        status = entry.get("status")
        if not isinstance(status, dict):
            continue

        if status.get("status") != "Claimed":
            continue

        claimed.append(
            {
                "site": status.get("site_name") or site_name,
                "url": status.get("url") or entry.get("url_user"),
                "rank": entry.get("rank", sys.maxsize),
                "http_status": entry.get("http_status"),
                "tags": status.get("tags") or [],
            }
        )

    claimed.sort(key=lambda item: (item["rank"], str(item["site"]).lower()))
    return claimed
