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

from colorama import Style
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException, TimeoutException

from helper import printer, timer

# How many results to fetch per query (user-selectable).
_RESULTS_CHOICES: dict[str, int] = {"1": 5, "2": 10, "3": 20, "4": 50}
_DEFAULT_MAX_RESULTS: int = 5

# Seconds to wait between consecutive queries to reduce rate-limit risk.
_INTER_QUERY_DELAY: float = 1.5

# Retry policy for transient errors.
_MAX_RETRIES: int = 3
_RETRY_BASE_DELAY: float = 4.0  # doubles on each attempt (exponential back-off)

# Directory where optional JSON exports are written.
_SAVE_DIR = Path("scraped_data")


@dataclass
class SearchResult:
    """One search result entry."""

    title: str
    url: str
    snippet: str = field(default="")
    label: str = field(default="")  # dork label / section the result came from


# Dork template tables
#
# Each entry is a (label, query_template) tuple.
# Templates reference placeholders that match keys in the *target* dict:
#   {query}    – raw query (General mode)
#   {name}     – full person name
#   {email}    – full e-mail address
#   {domain}   – domain name (auto-derived from e-mail when needed)
#   {username} – account handle / screen name
#   {phone}    – phone number string
#   {target}   – generic placeholder (Custom Dork mode)

_PERSON_DORKS: list[tuple[str, str]] = [
    ("General mention", '"{name}"'),
    ("LinkedIn", '"{name}" site:linkedin.com'),
    ("Twitter / X", '"{name}" (site:twitter.com OR site:x.com)'),
    ("Facebook", '"{name}" site:facebook.com'),
    ("Instagram", '"{name}" site:instagram.com'),
    ("GitHub", '"{name}" site:github.com'),
    ("YouTube", '"{name}" site:youtube.com'),
    ("Email links", '"{name}" email'),
    ("Phone links", '"{name}" phone'),
    ("News / press", '"{name}" (news OR article OR press OR interview)'),
    ("Public records", '"{name}" (address OR court OR record OR lawsuit)'),
    ("Images", '"{name}" photos OR pictures'),
]

_EMAIL_DORKS: list[tuple[str, str]] = [
    ("Direct mention", '"{email}"'),
    (
        "Paste sites",
        '"{email}" (site:pastebin.com OR site:ghostbin.com OR site:hastebin.com)',
    ),
    ("GitHub", '"{email}" site:github.com'),
    ("LinkedIn", '"{email}" site:linkedin.com'),
    ("Forum / community", '"{email}" (forum OR community OR post OR thread)'),
    ("Same-domain users", '"@{domain}" email'),
    ("Data breach mention", '"{email}" (breach OR leaked OR dump OR exposed)'),
    ("Registration traces", '"{email}" (register OR account OR signup OR profile)'),
]

_DOMAIN_DORKS: list[tuple[str, str]] = [
    ("All indexed pages", "site:{domain}"),
    ("Subdomains", "site:*.{domain}"),
    ("PDF documents", "site:{domain} filetype:pdf"),
    (
        "Office documents",
        "site:{domain} (filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:ppt)",
    ),
    (
        "Config / secrets",
        "site:{domain} (filetype:env OR filetype:conf OR filetype:bak OR filetype:cfg OR filetype:ini)",
    ),
    (
        "Admin panels",
        "site:{domain} (inurl:admin OR inurl:administrator OR inurl:wp-admin OR inurl:cpanel OR inurl:panel)",
    ),
    (
        "Login pages",
        "site:{domain} (inurl:login OR inurl:signin OR inurl:auth OR inurl:sso)",
    ),
    (
        "API endpoints",
        "site:{domain} (inurl:api OR inurl:v1 OR inurl:v2 OR inurl:graphql OR inurl:swagger)",
    ),
    ("Email addresses", '"@{domain}"'),
    ("Related / linked", "related:{domain}"),
    ("Mentions elsewhere", '"{domain}" -site:{domain}'),
    (
        "Tech stack hints",
        "site:{domain} (intext:powered OR intext:built OR intext:wordpress OR intext:shopify)",
    ),
]

_USERNAME_DORKS: list[tuple[str, str]] = [
    ("General mention", '"{username}"'),
    ("GitHub", 'site:github.com "{username}"'),
    ("Reddit", 'site:reddit.com/user "{username}"'),
    ("Twitter / X", '(site:twitter.com OR site:x.com) "{username}"'),
    ("Instagram", 'site:instagram.com "{username}"'),
    ("LinkedIn", 'site:linkedin.com/in "{username}"'),
    ("Steam", 'site:steamcommunity.com "{username}"'),
    ("Hacker News", 'site:news.ycombinator.com "{username}"'),
    (
        "Dev platforms",
        '(site:dev.to OR site:medium.com OR site:hashnode.dev) "{username}"',
    ),
    ("TikTok", 'site:tiktok.com "{username}"'),
    ("Twitch", 'site:twitch.tv "{username}"'),
    ("YouTube", 'site:youtube.com "{username}"'),
]

_PHONE_DORKS: list[tuple[str, str]] = [
    ("Direct mention", '"{phone}"'),
    ("Name / owner", '"{phone}" (name OR owner OR who OR person)'),
    ("TrueCaller", '"{phone}" site:truecaller.com'),
    (
        "Social profiles",
        '"{phone}" (site:linkedin.com OR site:facebook.com OR site:twitter.com)',
    ),
    (
        "Business listing",
        '"{phone}" (company OR business OR office OR ltd OR llc OR inc)',
    ),
    (
        "Public directory",
        '"{phone}" (directory OR whitepages OR yellowpages OR phonebook)',
    ),
    ("Address links", '"{phone}" (address OR location OR street)'),
    ("Paste / leak sites", "'{phone}' (site:pastebin.com OR site:ghostbin.com)"),
]

# Custom Dork mode uses a single user-supplied template; no pre-built list.
_CUSTOM_DORKS: list[tuple[str, str]] = []


# Mode registry
#
# Key → (display_name, dork_list, input_specs)
# input_specs: list of (prompt_label, target_dict_key) pairs.
# The first spec is the "primary" value shown in progress messages.

_ModeSpec = tuple[str, list[tuple[str, str]], list[tuple[str, str]]]

_MODES: dict[str, _ModeSpec] = {
    "1": ("General", [], [("Search query", "query")]),
    "2": ("Person", _PERSON_DORKS, [("Full name (e.g. Jane Doe)", "name")]),
    "3": ("Email", _EMAIL_DORKS, [("Email address", "email")]),
    "4": ("Domain", _DOMAIN_DORKS, [("Domain (e.g. example.com)", "domain")]),
    "5": ("Username", _USERNAME_DORKS, [("Username / handle", "username")]),
    "6": (
        "Phone Number",
        _PHONE_DORKS,
        [("Phone number (e.g. +13125550123)", "phone")],
    ),
    "7": (
        "Custom Dork",
        _CUSTOM_DORKS,
        [
            (
                "Dork template  (use {target} as placeholder, e.g. site:{target} filetype:pdf)",
                "template",
            ),
            ("Target value", "target"),
        ],
    ),
}


@timer.timer(require_input=True)
def websearch() -> None:
    """
    Interactive multi-mode OSINT web search powered by the ddgs library.

    Presents a mode-selection menu, collects relevant inputs, builds
    tailored dork queries, fetches results with automatic retry/back-off,
    deduplicates by URL, and displays grouped output.  Optionally exports
    all collected results to a timestamped JSON file in ``scraped_data/``.

    Modes
    -----
    1  General       – free-form query, single search
    2  Person        – 12 dorks for a person's online presence
    3  Email         – 8 dorks for e-mail OSINT
    4  Domain        – 12 dorks for website / domain reconnaissance
    5  Username      – 12 dorks across major platforms
    6  Phone Number  – 8 dorks for phone-number attribution
    7  Custom Dork   – user-defined dork template with a ``{target}`` slot
    """
    _print_mode_menu()

    mode_key = printer.user_input("Select mode [1-7] : ").strip()
    if mode_key not in _MODES:
        printer.error("Invalid mode. Please choose a number from 1 to 7.")
        return

    mode_name, dorks, input_spec = _MODES[mode_key]
    target: dict[str, str] = {}

    for label, key in input_spec:
        value = printer.user_input(f"{label} : ").strip()
        if not value:
            printer.error("Input cannot be empty.")
            return
        target[key] = value

    # Auto-derive domain from e-mail address.
    if "email" in target and "@" in target["email"] and "domain" not in target:
        target["domain"] = target["email"].split("@", 1)[1]

    # For Custom Dork mode, build a one-element dork list on the fly.
    if mode_key == "7":
        template = target.pop("template")
        dorks = [("Custom Dork", template)]

    primary_value = list(target.values())[0]
    max_results = _ask_max_results()
    save_fmt = _ask_save_results()

    printer.noprefix("")

    # General mode — single query
    if mode_key == "1":
        query = target["query"]
        printer.info(f"Searching for {Style.BRIGHT}{query}{Style.RESET_ALL}...")
        printer.noprefix("")
        printer.section("Web Search Results")

        results = _fetch_results(query, max_results, label="General")
        if not results:
            printer.warning(f"No results found for '{query}'.")
            return

        for result in results:
            _print_result(result)

        printer.info(f"Total results : {Style.BRIGHT}{len(results)}{Style.RESET_ALL}")

        if save_fmt:
            _save_results(results, mode_name, primary_value, save_fmt)
        return

    # OSINT dork modes (2–7)
    printer.info(
        f"Running {Style.BRIGHT}{mode_name}{Style.RESET_ALL} search for "
        f"{Style.BRIGHT}{primary_value}{Style.RESET_ALL}..."
    )
    printer.warning(
        f"Executing {len(dorks)} quer{'y' if len(dorks) == 1 else 'ies'} "
        f"({max_results} results each) with a {_INTER_QUERY_DELAY}s delay between "
        "each to reduce rate-limiting."
    )
    printer.noprefix("")
    printer.section(f"{mode_name} Search Results")

    seen_urls: set[str] = set()
    all_results: list[SearchResult] = []
    total_unique = 0

    for idx, (label, template) in enumerate(dorks, start=1):
        query = _build_query(template, target)
        printer.debug(f"[{idx}/{len(dorks)}] {label} → {query}")

        results = _fetch_results(query, max_results, label=label)
        new_results = [r for r in results if r.url not in seen_urls]

        if new_results:
            printer.noprefix("")
            printer.info(
                f"── [{idx}/{len(dorks)}] {label}  "
                f"({Style.BRIGHT}{len(new_results)}{Style.RESET_ALL} new)"
            )
            for result in new_results:
                seen_urls.add(result.url)
                all_results.append(result)
                total_unique += 1
                _print_result(result)
        else:
            printer.debug(f"No new results for [{label}]")

        if idx < len(dorks):
            time.sleep(_INTER_QUERY_DELAY)

    printer.noprefix("")
    printer.info(
        f"Search complete — "
        f"{Style.BRIGHT}{total_unique}{Style.RESET_ALL} unique result(s) across "
        f"{len(dorks)} quer{'y' if len(dorks) == 1 else 'ies'}."
    )

    if save_fmt and all_results:
        _save_results(all_results, mode_name, primary_value, save_fmt)
    elif save_fmt:
        printer.warning("No results to save.")


# Internal helpers


def _print_mode_menu() -> None:
    """Displays the mode selection menu."""
    printer.noprefix("")
    printer.section("Web Search — Select Mode")
    for key, (name, dorks, _) in _MODES.items():
        hint = f"({len(dorks)} dork queries)" if dorks else "(free-form)"
        printer.noprefix(f"   {Style.BRIGHT}[{key}]{Style.RESET_ALL} {name:<18} {hint}")
    printer.noprefix("")


def _ask_max_results() -> int:
    """Prompt the user to choose how many results to fetch per query."""
    printer.noprefix("")
    printer.info("Results per query:")
    for key, val in _RESULTS_CHOICES.items():
        printer.noprefix(f"   {Style.BRIGHT}[{key}]{Style.RESET_ALL} {val}")
    choice = printer.user_input("Select [1-4] (default = 1) : ").strip()
    selected = _RESULTS_CHOICES.get(choice, _DEFAULT_MAX_RESULTS)
    printer.debug(f"Max results per query set to {selected}.")
    return selected


def _ask_save_results() -> str | None:
    """
    Ask whether to export collected results and, if so, in which format.

    :return: ``'txt'``, ``'csv'``, or ``'json'`` if the user wants to save;
             ``None`` if they decline.
    """
    answer = printer.user_input("Save results to file? (y/N) : ").strip().lower()
    if answer not in {"y", "yes"}:
        return None

    printer.noprefix("")
    printer.section("Export Format")
    printer.info("  1 : TXT  (plain text)")
    printer.info("  2 : CSV  (comma-separated values)")
    printer.info("  3 : JSON (structured data)")

    format_map = {"1": "txt", "2": "csv", "3": "json", "": "txt"}
    choice = printer.user_input("Choose format (1/2/3) [default: 1] : ").strip()
    return format_map.get(choice, "txt")


def _save_results(
    results: list[SearchResult],
    mode_name: str,
    target: str,
    fmt: str = "json",
) -> None:
    """
    Export *results* to a timestamped file under ``scraped_data/``.

    :param results:   List of :class:`SearchResult` objects to persist.
    :param mode_name: Human-readable mode name used in the filename.
    :param target:    Primary target value used in the filename.
    :param fmt:       Export format — ``'txt'``, ``'csv'``, or ``'json'``.
    """
    _SAVE_DIR.mkdir(exist_ok=True)

    slug = (
        mode_name.lower().replace(" ", "_")
        + "_"
        + "".join(c if c.isalnum() or c in "-_." else "_" for c in target)[:40]
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        match fmt.lower():
            case "txt":
                filepath = _SAVE_DIR / f"websearch_{slug}_{timestamp}.txt"
                with filepath.open("w", encoding="utf-8") as fh:
                    fh.write(f"Deep Web Search — {mode_name}\n")
                    fh.write(f"Target  : {target}\n")
                    fh.write(
                        f"Date    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    fh.write(f"Results : {len(results)}\n")
                    fh.write("-" * 80 + "\n\n")
                    for r in results:
                        fh.write(f"[{r.label}]\n" if r.label else "")
                        fh.write(f"Title   : {r.title}\n")
                        fh.write(f"URL     : {r.url}\n")
                        if r.snippet:
                            fh.write(f"Snippet : {r.snippet}\n")
                        fh.write("\n")
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "csv":
                filepath = _SAVE_DIR / f"websearch_{slug}_{timestamp}.csv"
                with filepath.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["Label", "Title", "URL", "Snippet"])
                    for r in results:
                        writer.writerow([r.label, r.title, r.url, r.snippet])
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "json":
                filepath = _SAVE_DIR / f"websearch_{slug}_{timestamp}.json"
                payload = {
                    "mode": mode_name,
                    "target": target,
                    "timestamp": datetime.now().isoformat(),
                    "total_results": len(results),
                    "results": [asdict(r) for r in results],
                }
                with filepath.open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case _:
                printer.error(f"Unknown format '{fmt}'. Use 'txt', 'csv', or 'json'.")

    except OSError as exc:
        printer.error(f"Could not write results file: {exc}")


def _build_query(template: str, target: dict[str, str]) -> str:
    """
    Fill a dork template with values from *target*.

    Unknown placeholders are silently left as-is so a partially-filled
    template still produces a runnable (if suboptimal) query string.

    :param template: Dork template containing ``{placeholder}`` fields.
    :param target:   Mapping of placeholder names → values.
    :return: Formatted query string.
    """
    try:
        return template.format(**target)
    except KeyError:
        return template


def _fetch_results(
    query: str,
    max_results: int,
    *,
    label: str = "",
) -> list[SearchResult]:
    """
    Fetch text search results via the ``ddgs`` library with exponential
    back-off retry on rate-limit and timeout errors.

    :param query:       The search query string.
    :param max_results: Maximum number of results to request.
    :param label:       Section label attached to each :class:`SearchResult`.
    :return:            List of :class:`SearchResult` objects.
    """
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            with DDGS() as ddgs:
                raw: list[dict] = ddgs.text(query, max_results=max_results) or []

            return [
                SearchResult(
                    title=r.get("title", "").strip(),
                    url=r.get("href", "").strip(),
                    snippet=r.get("body", "").strip(),
                    label=label,
                )
                for r in raw
                if r.get("href", "").strip()
            ]

        except RatelimitException:
            delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
            printer.warning(
                f"Rate limited — waiting {delay:.0f}s "
                f"(attempt {attempt}/{_MAX_RETRIES})..."
            )
            time.sleep(delay)

        except TimeoutException:
            printer.warning(f"Request timed out (attempt {attempt}/{_MAX_RETRIES}).")
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BASE_DELAY)

        except DDGSException as exc:
            printer.error(f"Search error: {exc}")
            return []

        except Exception as exc:  # noqa: BLE001
            printer.error(f"Unexpected error during search: {exc}")
            return []

    printer.error(
        f"All {_MAX_RETRIES} attempts failed"
        + (f" for [{label}]" if label else "")
        + "."
    )
    return []


def _print_result(result: SearchResult) -> None:
    """
    Print a single :class:`SearchResult` in the standard toolkit layout::

        [+] Bold Title
                https://example.com/path
                Snippet text, truncated to 220 chars if needed…

    :param result: The result to render.
    """
    printer.success(f"{Style.BRIGHT}{result.title}{Style.RESET_ALL}")
    printer.noprefix(f"    {result.url}")
    if result.snippet:
        snippet = (
            result.snippet
            if len(result.snippet) <= 220
            else result.snippet[:217] + "..."
        )
        printer.noprefix(f"    {snippet}")
    printer.noprefix("")
