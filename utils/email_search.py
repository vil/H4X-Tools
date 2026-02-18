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

import re
import subprocess
from dataclasses import dataclass, field

from colorama import Style

from helper import printer, timer

# Basic RFC-5321-ish pattern — catches obvious typos without being overly
# strict.  Proper validation would require actually sending a test message.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Matches holehe's footer stat line, e.g. "118 websites checked in 4.32 seconds"
_STATS_RE = re.compile(r"^(\d+)\s+websites?\s+checked\s+in\s+([\d.]+)\s+seconds?", re.I)

# Matches a result line like:
#   [+] adobe.com recovery@other.com / +1234567890 / FullName John Doe
#   [-] twitter.com
#   [x] netflix.com
_RESULT_RE = re.compile(r"^\[(\+|-|x)\]\s+(\S+)(.*)?$")


@dataclass
class HoleheSite:
    """Represents a single holehe result entry."""

    domain: str
    found: bool
    rate_limited: bool
    # Extra data holehe may recover: recovery email, phone number, full name, etc.
    extra: str = field(default="")


@timer.timer(require_input=True)
def search(email: str) -> None:
    """
    Searches for registered accounts linked to an email address using holehe.

    Validates the email format, runs holehe with clean output flags, then
    displays a structured summary of every site where the address was found,
    including any extra data holehe could recover (recovery email, phone
    number, full name, account creation date).

    Thanks to Holehe — https://github.com/megadose/holehe

    :param email: The email address to search for.
    """
    email = email.strip().lower()

    if not _validate_email(email):
        return

    printer.info(
        f"Searching for accounts linked to {Style.BRIGHT}{email}{Style.RESET_ALL}..."
    )

    _run_holehe(email)


# Internal helpers


def _validate_email(email: str) -> bool:
    """
    Performs basic email format validation.

    :param email: The email address to check.
    :return: ``True`` if the format looks valid, ``False`` otherwise.
    """
    if not _EMAIL_RE.match(email):
        printer.error(f"'{email}' does not look like a valid email address.")
        printer.info("Expected format: user@example.com")
        return False
    return True


def _run_holehe(email: str) -> None:
    """
    Invokes the holehe CLI and prints the parsed results.

    Flags used:

    * ``--only-used``  — suppress not-found (``[-]``) lines; show only hits
    * ``--no-color``   — plain-text output for reliable parsing
    * ``--no-clear``   — do not wipe the terminal before printing results

    :param email: The validated email address.
    """
    try:
        result = subprocess.run(
            [
                "holehe",
                email,
                "--only-used",
                "--no-color",
                "--no-clear",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        combined = result.stdout + result.stderr

        if not combined.strip():
            printer.warning("holehe returned no output.")
            return

        sites, stats = _parse_holehe_output(combined)
        _print_results(sites, stats)
        printer.info("Credits to megadose (Palenath) for holehe.")

    except FileNotFoundError:
        printer.error(
            f"{Style.BRIGHT}holehe{Style.RESET_ALL} was not found. "
            f"Install it with: {Style.BRIGHT}pip install holehe{Style.RESET_ALL}"
        )
    except subprocess.TimeoutExpired:
        printer.error(
            "holehe timed out after 120 seconds. "
            "Try again or check your internet connection."
        )
    except subprocess.CalledProcessError as exc:
        printer.error(f"holehe exited with a non-zero status: {exc}")
    except Exception as exc:
        printer.error(f"Unexpected error while running holehe: {exc}")


def _parse_holehe_output(output: str) -> tuple[list[HoleheSite], str]:
    """
    Parses holehe's plain-text output into structured :class:`HoleheSite`
    objects and an optional stats string.

    Holehe result-line conventions (with ``--only-used``, ``[-]`` lines are
    suppressed by holehe itself, but we guard against them regardless):

    * ``[+] domain.com [extra…]`` — email **is** registered; may carry
      a recovery email, phone number, full name, or creation date inline.
    * ``[-] domain.com``          — email is *not* registered (filtered out).
    * ``[x] domain.com``          — rate limited; result unknown.

    Footer stat line example::

        118 websites checked in 4.32 seconds

    :param output: Raw captured stdout from holehe.
    :return: Tuple of ``(sites, stats_line)`` where *sites* is sorted by
             domain and *stats_line* is the footer string (empty if absent).
    """
    # Strip any residual ANSI escape codes that slip through despite --no-color.
    ansi_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    sites: list[HoleheSite] = []
    stats = ""

    for line in output.splitlines():
        clean = ansi_re.sub("", line).strip()
        if not clean:
            continue

        # Footer stats line
        if _STATS_RE.match(clean):
            stats = clean
            continue

        match = _RESULT_RE.match(clean)
        if not match:
            continue

        symbol, domain, extra_raw = match.group(1), match.group(2), match.group(3) or ""

        # Holehe prints a legend line at the bottom:
        #   [+] Email used, [-] Email not used, [x] Rate limit
        # _RESULT_RE matches it with domain="Email" (no dot).  Real domains
        # always contain at least one dot, so we use that to skip it.
        if "." not in domain:
            continue

        extra = extra_raw.strip().lstrip("/").strip()

        if symbol == "+":
            sites.append(
                HoleheSite(domain=domain, found=True, rate_limited=False, extra=extra)
            )
        elif symbol == "x":
            sites.append(
                HoleheSite(domain=domain, found=False, rate_limited=True, extra=extra)
            )
        # "-" (not found) is intentionally ignored — holehe suppresses these
        # with --only-used, but skip them explicitly for robustness.

    sites.sort(key=lambda s: s.domain)
    return sites, stats


def _print_results(sites: list[HoleheSite], stats: str) -> None:
    """
    Displays the parsed holehe results with counts and extra recovered data.

    :param sites: Parsed list of :class:`HoleheSite` objects.
    :param stats: Footer stats string from holehe (may be empty).
    """
    found = [s for s in sites if s.found]
    rate_limited = [s for s in sites if s.rate_limited]

    printer.noprefix("")
    printer.section("Holehe Results")

    if found:
        printer.info(
            f"Registered on {Style.BRIGHT}{len(found)}{Style.RESET_ALL} site(s):"
        )
        for site in found:
            # Build the display line; append any extra data holehe recovered.
            line = f"  {Style.BRIGHT}{site.domain}{Style.RESET_ALL}"
            if site.extra:
                line += f"  ({_format_extra(site.extra)})"
            printer.success(line)
    else:
        printer.warning("Not found on any sites.")

    if rate_limited:
        printer.noprefix("")
        printer.warning(
            f"Rate limited on {Style.BRIGHT}{len(rate_limited)}{Style.RESET_ALL} "
            "site(s) — could not determine registration status:"
        )
        for site in rate_limited:
            printer.warning(f"  [x] {site.domain}")

    if stats:
        printer.noprefix("")
        printer.info(stats)


def _format_extra(raw: str) -> str:
    """
    Converts holehe's inline extra string into a human-readable label.

    Holehe concatenates extra fields with `` / `` separators, e.g.::

        recovery@other.com / +1234567890 / FullName John Doe

    This function splits on those separators and returns a tidy comma-joined
    string with labelled fields where possible.

    :param raw: The raw extra string from the holehe output line.
    :return: Formatted string, e.g.
             ``"recovery: recovery@other.com, phone: +1234567890, name: John Doe"``.
    """
    # Holehe joins fields with " / " (space-slash-space).  Splitting on bare
    # "/" would break URLs like "https://gravatar.com/username", so we use
    # the full " / " separator instead.
    parts = [p.strip() for p in raw.split(" / ") if p.strip()]
    labelled: list[str] = []

    for part in parts:
        if part.startswith("FullName "):
            labelled.append(f"name: {part[len('FullName ') :]}")
        elif part.startswith("Date, time of the creation "):
            labelled.append(f"created: {part[len('Date, time of the creation ') :]}")
        elif re.match(r"^\+?\d[\d\s\-().]{6,}$", part):
            labelled.append(f"phone: {part}")
        elif "@" in part:
            labelled.append(f"recovery: {part}")
        else:
            labelled.append(part)

    return ", ".join(labelled)
