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
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import requests
from colorama import Style

from helper import printer, randomuser, timer

_REQUEST_TIMEOUT: int = 20
_MAX_RETRIES: int = 3
_RETRY_BASE_DELAY: float = 3.0

_SAVE_DIR = Path("scraped_data")

# How many stealer/credential entries to display inline (user-selectable).
_ENTRY_LIMIT_CHOICES: dict[str, int | None] = {
    "1": 3,
    "2": 5,
    "3": 10,
    "4": None,  # all
}
_DEFAULT_ENTRY_LIMIT: int = 5

# Hudson Rock Cavalier API base URL.
_HR_BASE = "https://cavalier.hudsonrock.com/api/json/v2/osint-tools"

# ProxyNova COMB (Collection Of Many Breaches) — email-only, no key needed.
_PN_BASE = "https://api.proxynova.com/comb"


@dataclass
class StealerEntry:
    """One stealer-log record returned by Hudson Rock."""

    date_compromised: str = ""
    stealer_family: str = ""
    computer_name: str = ""
    operating_system: str = ""
    ip: str = ""
    malware_path: str = ""
    antiviruses: list[str] = field(default_factory=list)
    top_logins: list[str] = field(default_factory=list)
    top_passwords: list[str] = field(default_factory=list)
    total_corporate_services: int = 0
    total_user_services: int = 0


@dataclass
class CombEntry:
    """One credential line from the ProxyNova COMB dataset."""

    line: str = ""  # raw "email:password" string
    email: str = ""
    password: str = ""


@dataclass
class LeakReport:
    """Aggregated results from all sources for a single target."""

    target: str = ""
    target_type: str = ""  # "email" | "domain" | "username"
    # Hudson Rock
    hr_message: str = ""
    hr_stealers: list[StealerEntry] = field(default_factory=list)
    hr_employees: list[dict] = field(default_factory=list)
    hr_users: list[dict] = field(default_factory=list)
    # ProxyNova COMB (email only)
    comb_count: int = 0
    comb_entries: list[CombEntry] = field(default_factory=list)


# Target-type detection


def _detect_type(target: str) -> str:
    """
    Infer whether *target* is an e-mail address, a domain, or a username.

    :param target: Raw input string from the user.
    :return: ``'email'``, ``'domain'``, or ``'username'``.
    """
    if "@" in target:
        return "email"
    if "." in target and " " not in target:
        return "domain"
    return "username"


# HTTP helpers


def _get(url: str, params: dict | None = None) -> dict | None:
    """
    Performs a GET request with retry / exponential back-off.

    :param url:    Full URL to request.
    :param params: Optional query-string parameters.
    :return:       Parsed JSON dict, or ``None`` on permanent failure.
    """
    headers = {"User-Agent": str(randomuser.GetUser())}
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=_REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
            printer.warning(
                f"Request timed out (attempt {attempt}/{_MAX_RETRIES}). "
                f"Retrying in {delay:.0f}s..."
            )
            time.sleep(delay)
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return {}  # target not found — not an error
            printer.error(f"HTTP error: {exc}")
            return None
        except requests.exceptions.RequestException as exc:
            printer.error(f"Request failed: {exc}")
            return None
    printer.error(f"All {_MAX_RETRIES} attempts failed for {url}.")
    return None


# Hudson Rock fetching & parsing


def _fetch_hudson_rock(
    target: str, target_type: str
) -> tuple[str, list[StealerEntry], list[dict], list[dict]]:
    """
    Query the Hudson Rock Cavalier API for *target*.

    :param target:      The value to search for.
    :param target_type: ``'email'``, ``'domain'``, or ``'username'``.
    :return: Tuple of (message, stealers, employees, users).
    """
    endpoint_map = {
        "email": f"{_HR_BASE}/search-by-email",
        "domain": f"{_HR_BASE}/search-by-domain",
        "username": f"{_HR_BASE}/search-by-username",
    }
    param_map = {
        "email": "email",
        "domain": "domain",
        "username": "username",
    }

    url = endpoint_map[target_type]
    param_key = param_map[target_type]

    printer.debug(f"Hudson Rock → {url}?{param_key}={target}")
    data = _get(url, params={param_key: target})

    if data is None:
        return "", [], [], []
    if not data:
        return "", [], [], []

    message: str = data.get("message", "")

    # Top-level stealers (email / username responses)
    raw_stealers: list[dict] = data.get("stealers", []) or []
    stealers = [_parse_stealer(s) for s in raw_stealers]

    # Prepare employees/users lists (domain responses use different shapes)
    employees: list[dict] = []
    users: list[dict] = []

    # If domain-style response contains a "data" dict
    data_block = data.get("data")
    if isinstance(data_block, dict):
        # Prefer detailed all_urls entries which include type/occurrence
        all_urls = data_block.get("all_urls") or []
        if isinstance(all_urls, list) and all_urls:
            for item in all_urls:
                try:
                    t = (item.get("type") or "").lower()
                    rec = {
                        "url": item.get("url", "") or "",
                        "occurrence": int(item.get("occurrence") or 0),
                    }
                except Exception:
                    # Skip malformed items
                    continue
                if t == "employee":
                    employees.append(rec)
                elif t == "user":
                    users.append(rec)
            # Return early; employees/users built from all_urls
            return message, stealers, employees, users

        # Fallback to employees_urls / clients_urls arrays with occurrence/type
        emp_urls = data_block.get("employees_urls") or []
        if isinstance(emp_urls, list):
            for item in emp_urls:
                if not isinstance(item, dict):
                    continue
                employees.append(
                    {
                        "url": item.get("url", "") or "",
                        "occurrence": int(item.get("occurrence") or 0),
                    }
                )
        client_urls = data_block.get("clients_urls") or []
        if isinstance(client_urls, list):
            for item in client_urls:
                if not isinstance(item, dict):
                    continue
                users.append(
                    {
                        "url": item.get("url", "") or "",
                        "occurrence": int(item.get("occurrence") or 0),
                    }
                )
        # Continue to return at end after attempting data_block parsing

    # If there's a stats block with URL lists (less detailed)
    stats = data.get("stats")
    if (not employees and not users) and isinstance(stats, dict):
        emp_stats_urls = stats.get("employees_urls") or []
        if isinstance(emp_stats_urls, list):
            for u in emp_stats_urls:
                if isinstance(u, str):
                    employees.append({"url": u, "occurrence": None})
        client_stats_urls = stats.get("clients_urls") or []
        if isinstance(client_stats_urls, list):
            for u in client_stats_urls:
                if isinstance(u, str):
                    users.append({"url": u, "occurrence": None})

    # Some responses include top-level numeric counts for employees/users - don't treat as lists
    # Normalize any accidental scalar values from data.get("employees") / data.get("users")
    raw_employees = data.get("employees")
    raw_users = data.get("users")
    if isinstance(raw_employees, list) and not employees:
        for item in raw_employees:
            if isinstance(item, dict):
                employees.append(
                    {
                        "url": item.get("url", "") or "",
                        "occurrence": int(item.get("occurrence") or 0),
                    }
                )
    if isinstance(raw_users, list) and not users:
        for item in raw_users:
            if isinstance(item, dict):
                users.append(
                    {
                        "url": item.get("url", "") or "",
                        "occurrence": int(item.get("occurrence") or 0),
                    }
                )

    # Final normalization: ensure lists are lists (empty if nothing found)
    if employees is None:
        employees = []
    if users is None:
        users = []

    return message, stealers, employees, users


def _parse_stealer(raw: dict) -> StealerEntry:
    """
    Convert a raw Hudson Rock stealer dict into a typed :class:`StealerEntry`.

    :param raw: Dict from the API response.
    :return:    Populated :class:`StealerEntry`.
    """
    return StealerEntry(
        date_compromised=raw.get("date_compromised", ""),
        stealer_family=raw.get("stealer_family", "Unknown"),
        computer_name=raw.get("computer_name", ""),
        operating_system=raw.get("operating_system", ""),
        ip=raw.get("ip", ""),
        malware_path=raw.get("malware_path", ""),
        antiviruses=raw.get("antiviruses") or [],
        top_logins=raw.get("top_logins") or [],
        top_passwords=raw.get("top_passwords") or [],
        total_corporate_services=int(raw.get("total_corporate_services") or 0),
        total_user_services=int(raw.get("total_user_services") or 0),
    )


# ProxyNova COMB fetching & parsing


def _fetch_comb(email: str) -> tuple[int, list[CombEntry]]:
    """
    Query the ProxyNova COMB dataset for *email*.

    :param email: E-mail address to look up.
    :return: Tuple of (total_count, list of :class:`CombEntry`).
    """
    printer.debug(f"ProxyNova COMB → {_PN_BASE}?query={email}")
    data = _get(_PN_BASE, params={"query": email})

    if not data:
        return 0, []

    count: int = int(data.get("count") or 0)
    lines: list[str] = data.get("lines") or []

    entries: list[CombEntry] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Format is  email:password  — split on the first colon only.
        if ":" in line:
            _, _, password = line.partition(":")
        else:
            password = ""
        entries.append(CombEntry(line=line, email=email, password=password))

    return count, entries


# Display helpers


def _print_stealer(entry: StealerEntry, index: int, total: int) -> None:
    """Print one :class:`StealerEntry` in a clearly labelled block."""
    printer.info(f"  Entry {index}/{total}")
    printer.success(f"    {'Date compromised':<22} : {entry.date_compromised or 'N/A'}")
    printer.success(f"    {'Stealer family':<22} : {entry.stealer_family or 'N/A'}")
    printer.success(f"    {'Computer':<22} : {entry.computer_name or 'N/A'}")
    printer.success(f"    {'OS':<22} : {entry.operating_system or 'N/A'}")
    printer.success(f"    {'IP address':<22} : {entry.ip or 'N/A'}")
    printer.success(f"    {'Malware path':<22} : {entry.malware_path or 'N/A'}")
    if entry.antiviruses:
        printer.success(f"    {'Antiviruses':<22} : {', '.join(entry.antiviruses)}")
    printer.success(
        f"    {'Corporate services':<22} : {entry.total_corporate_services}"
    )
    printer.success(f"    {'User services':<22} : {entry.total_user_services}")
    if entry.top_logins:
        printer.success(f"    {'Top logins':<22} : {', '.join(entry.top_logins)}")
    if entry.top_passwords:
        printer.success(f"    {'Top passwords':<22} : {', '.join(entry.top_passwords)}")
    printer.noprefix("")


def _print_comb_entry(entry: CombEntry, index: int) -> None:
    """Print one :class:`CombEntry`."""
    printer.success(f"  [{index:>3}] {entry.line}")


# Export


def _ask_export() -> str | None:
    """
    Ask the user whether and in what format to export the report.

    :return: ``'txt'``, ``'csv'``, or ``'json'``; ``None`` if declined.
    """
    answer = printer.user_input("Save results to file? (y/N) : ").strip().lower()
    if answer not in {"y", "yes"}:
        return None

    printer.noprefix("")
    printer.section("Export Format")
    printer.info("  1 : TXT  (plain text report)")
    printer.info("  2 : CSV  (spreadsheet-friendly)")
    printer.info("  3 : JSON (full structured data)")

    fmt_map = {"1": "txt", "2": "csv", "3": "json", "": "txt"}
    choice = printer.user_input("Choose format (1/2/3) [default: 1] : ").strip()
    return fmt_map.get(choice, "txt")


def _export(report: LeakReport, fmt: str) -> None:
    """
    Write *report* to ``scraped_data/`` in the requested format.

    :param report: The fully populated :class:`LeakReport`.
    :param fmt:    ``'txt'``, ``'csv'``, or ``'json'``.
    """
    _SAVE_DIR.mkdir(exist_ok=True)

    slug = "".join(c if c.isalnum() or c in "-_." else "_" for c in report.target)[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        match fmt.lower():
            case "txt":
                filepath = _SAVE_DIR / f"leaksearch_{slug}_{timestamp}.txt"
                with filepath.open("w", encoding="utf-8") as fh:
                    fh.write("Leak Search Report\n")
                    fh.write(f"Target      : {report.target}\n")
                    fh.write(f"Type        : {report.target_type}\n")
                    fh.write(
                        f"Date        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    fh.write("=" * 80 + "\n\n")

                    # Hudson Rock stealers
                    fh.write(
                        f"HUDSON ROCK  ({len(report.hr_stealers)} stealer record(s))\n"
                    )
                    fh.write("-" * 80 + "\n")
                    if report.hr_message:
                        fh.write(f"Note: {report.hr_message}\n\n")
                    for i, s in enumerate(report.hr_stealers, 1):
                        fh.write(f"  [{i}] Date       : {s.date_compromised}\n")
                        fh.write(f"      Stealer    : {s.stealer_family}\n")
                        fh.write(f"      Computer   : {s.computer_name}\n")
                        fh.write(f"      OS         : {s.operating_system}\n")
                        fh.write(f"      IP         : {s.ip}\n")
                        fh.write(f"      Corp svcs  : {s.total_corporate_services}\n")
                        fh.write(f"      User svcs  : {s.total_user_services}\n")
                        fh.write(f"      Logins     : {', '.join(s.top_logins)}\n")
                        fh.write(f"      Passwords  : {', '.join(s.top_passwords)}\n")
                        fh.write("\n")

                    # Domain-mode employees / users
                    if report.hr_employees or report.hr_users:
                        fh.write(
                            f"\nEMPLOYEES ({len(report.hr_employees)}) / "
                            f"USERS ({len(report.hr_users)})\n"
                        )
                        fh.write("-" * 80 + "\n")
                        for rec in report.hr_employees + report.hr_users:
                            for k, v in rec.items():
                                fh.write(f"  {k:<20}: {v}\n")
                            fh.write("\n")

                    # COMB
                    if report.comb_count:
                        fh.write(
                            f"\nPROXYNOVA COMB  ({report.comb_count} total hit(s))\n"
                        )
                        fh.write("-" * 80 + "\n")
                        for entry in report.comb_entries:
                            fh.write(f"  {entry.line}\n")

                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "csv":
                filepath = _SAVE_DIR / f"leaksearch_{slug}_{timestamp}.csv"
                with filepath.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    # Hudson Rock stealers sheet
                    writer.writerow(
                        [
                            "source",
                            "date_compromised",
                            "stealer_family",
                            "computer_name",
                            "operating_system",
                            "ip",
                            "total_corporate_services",
                            "total_user_services",
                            "top_logins",
                            "top_passwords",
                        ]
                    )
                    for s in report.hr_stealers:
                        writer.writerow(
                            [
                                "hudson_rock",
                                s.date_compromised,
                                s.stealer_family,
                                s.computer_name,
                                s.operating_system,
                                s.ip,
                                s.total_corporate_services,
                                s.total_user_services,
                                " | ".join(s.top_logins),
                                " | ".join(s.top_passwords),
                            ]
                        )
                    # COMB entries
                    if report.comb_entries:
                        writer.writerow([])
                        writer.writerow(["source", "line", "email", "password"])
                        for entry in report.comb_entries:
                            writer.writerow(
                                [
                                    "proxynova_comb",
                                    entry.line,
                                    entry.email,
                                    entry.password,
                                ]
                            )
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "json":
                filepath = _SAVE_DIR / f"leaksearch_{slug}_{timestamp}.json"
                payload = {
                    "target": report.target,
                    "target_type": report.target_type,
                    "timestamp": datetime.now().isoformat(),
                    "hudson_rock": {
                        "total_stealers": len(report.hr_stealers),
                        "message": report.hr_message,
                        "stealers": [asdict(s) for s in report.hr_stealers],
                        "employees": report.hr_employees,
                        "users": report.hr_users,
                    },
                    "proxynova_comb": {
                        "total_hits": report.comb_count,
                        "entries": [asdict(e) for e in report.comb_entries],
                    },
                }
                with filepath.open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case _:
                printer.error(f"Unknown format '{fmt}'. Use 'txt', 'csv', or 'json'.")

    except OSError as exc:
        printer.error(f"Could not write file: {exc}")


def _ask_entry_limit() -> int | None:
    """
    Ask how many stealer/credential entries to display inline.

    :return: An integer cap, or ``None`` meaning "show all".
    """
    printer.noprefix("")
    printer.info("Entries to display per source:")
    for key, val in _ENTRY_LIMIT_CHOICES.items():
        label = str(val) if val is not None else "all"
        printer.noprefix(f"   {Style.BRIGHT}[{key}]{Style.RESET_ALL} {label}")
    choice = printer.user_input("Select [1-4] (default = 2) : ").strip()
    return _ENTRY_LIMIT_CHOICES.get(choice, _DEFAULT_ENTRY_LIMIT)


@timer.timer(require_input=True)
def lookup(target: str) -> None:
    """
    Multi-source leak and breach search for an e-mail, domain, or username.

    Sources
    -------
    - **Hudson Rock Cavalier API** — stealer-log intelligence (email, domain,
      username). Returns infected-computer records including date of compromise,
      stealer family, machine details, and masked credential samples.
    - **ProxyNova COMB** — Collection Of Many Breaches credential dataset
      (email only). Returns the total number of hits and raw credential lines.

    :param target: E-mail address, domain name, or username to investigate.
    """
    target = target.strip()
    if not target:
        printer.error("Target cannot be empty.")
        return

    target_type = _detect_type(target)
    printer.info(
        f"Target {Style.BRIGHT}{target}{Style.RESET_ALL} "
        f"detected as {Style.BRIGHT}{target_type}{Style.RESET_ALL}."
    )

    entry_limit = _ask_entry_limit()
    report = LeakReport(target=target, target_type=target_type)

    # Source 1 — Hudson Rock                                               #
    printer.noprefix("")
    printer.section("Hudson Rock Cavalier")
    printer.info(f"Querying Hudson Rock for {Style.BRIGHT}{target}{Style.RESET_ALL}...")

    hr_msg, hr_stealers, hr_employees, hr_users = _fetch_hudson_rock(
        target, target_type
    )
    report.hr_message = hr_msg
    report.hr_stealers = hr_stealers
    report.hr_employees = hr_employees or []
    report.hr_users = hr_users or []

    if hr_stealers:
        printer.success(
            f"Found {Style.BRIGHT}{len(hr_stealers)}{Style.RESET_ALL} "
            "stealer record(s)."
        )
        if hr_msg:
            printer.warning(hr_msg)
        printer.noprefix("")

        display_count = (
            len(hr_stealers)
            if entry_limit is None
            else min(entry_limit, len(hr_stealers))
        )
        for i, entry in enumerate(hr_stealers[:display_count], 1):
            _print_stealer(entry, i, len(hr_stealers))

        if display_count < len(hr_stealers):
            printer.info(
                f"  ... {len(hr_stealers) - display_count} more record(s) not shown "
                "(export to see all)."
            )

    elif hr_employees or hr_users:
        printer.debug(hr_employees, hr_users)

        emp_count = len(hr_employees) if isinstance(hr_employees, (list, tuple)) else 0
        user_count = len(hr_users) if isinstance(hr_users, (list, tuple)) else 0

        printer.success(
            f"Found {Style.BRIGHT}{emp_count}{Style.RESET_ALL} "
            f"employee(s) and "
            f"{Style.BRIGHT}{user_count}{Style.RESET_ALL} user(s)."
        )
        printer.noprefix("")

        all_records = hr_employees + hr_users
        display_count = (
            len(all_records)
            if entry_limit is None
            else min(entry_limit, len(all_records))
        )
        for rec in all_records[:display_count]:
            for k, v in rec.items():
                label = k.replace("_", " ").title()
                printer.success(f"    {label:<22} : {v}")
            printer.noprefix("")

        if display_count < len(all_records):
            printer.info(
                f"  ... {len(all_records) - display_count} more record(s) not shown "
                "(export to see all)."
            )

    else:
        printer.warning("No stealer records found on Hudson Rock for this target.")

    # Source 2 — ProxyNova COMB (email only)                              #
    if target_type == "email":
        printer.noprefix("")
        printer.section("ProxyNova COMB Dataset")
        printer.info(
            f"Querying COMB dataset for {Style.BRIGHT}{target}{Style.RESET_ALL}..."
        )

        comb_count, comb_entries = _fetch_comb(target)
        report.comb_count = comb_count
        report.comb_entries = comb_entries

        if comb_count:
            printer.success(
                f"Found {Style.BRIGHT}{comb_count:,}{Style.RESET_ALL} "
                "credential hit(s) in the COMB dataset."
            )
            printer.noprefix("")

            display_count = (
                len(comb_entries)
                if entry_limit is None
                else min(entry_limit, len(comb_entries))
            )
            for i, entry in enumerate(comb_entries[:display_count], 1):
                _print_comb_entry(entry, i)

            if display_count < len(comb_entries):
                printer.info(
                    f"  ... {len(comb_entries) - display_count} more line(s) not shown "
                    "(export to see all)."
                )
        else:
            printer.warning("No entries found in the COMB dataset for this address.")

    # Summary                                                              #
    printer.noprefix("")
    printer.section("Summary")
    printer.info(f"Target        : {Style.BRIGHT}{target}{Style.RESET_ALL}")
    printer.info(f"Type          : {target_type}")
    printer.info(
        f"HR stealers   : {Style.BRIGHT}{len(report.hr_stealers)}{Style.RESET_ALL}"
    )
    if target_type == "domain":
        printer.info(
            f"HR employees  : {Style.BRIGHT}{len(report.hr_employees)}{Style.RESET_ALL}"
        )
        printer.info(
            f"HR users      : {Style.BRIGHT}{len(report.hr_users)}{Style.RESET_ALL}"
        )
    if target_type == "email":
        printer.info(
            f"COMB hits     : {Style.BRIGHT}{report.comb_count:,}{Style.RESET_ALL}"
        )

    # Export                                                               #
    printer.noprefix("")
    fmt = _ask_export()
    if fmt:
        _export(report, fmt)
    printer.noprefix("")
    printer.info(
        f"Hudson Rock raw data : "
        f"{Style.BRIGHT}https://cavalier.hudsonrock.com{Style.RESET_ALL}"
    )
