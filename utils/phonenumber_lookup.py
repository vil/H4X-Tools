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
import time

import phonenumbers as p
from colorama import Style
from phonenumbers import (
    PhoneNumberType,
    carrier,
    geocoder,
    number_type,
    timezone,
)

from helper import printer, timer

# Human-readable labels for every PhoneNumberType variant.
# PhoneNumberType is an int alias, not a true enum, so the dict is keyed by int.
_NUMBER_TYPE_LABELS: dict[int, str] = {
    PhoneNumberType.MOBILE: "Mobile",
    PhoneNumberType.FIXED_LINE: "Fixed Line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
    PhoneNumberType.TOLL_FREE: "Toll-Free",
    PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    PhoneNumberType.SHARED_COST: "Shared Cost",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    PhoneNumberType.PAGER: "Pager",
    PhoneNumberType.UAN: "UAN",
    PhoneNumberType.VOICEMAIL: "Voicemail",
    PhoneNumberType.UNKNOWN: "Unknown",
}


@timer.timer(require_input=True)
def lookup(phone_number: str) -> None:
    """
    Looks up a phone number and checks it across OSINT sources.

    Performs structured number analysis via the phonenumbers library (formats,
    validity, type, carrier, region, time zones) and then uses *ignorant* to
    check whether the number is registered on known social-media platforms.

    :param phone_number: The phone number to look up.  Should include the
                         country code, e.g. ``+358501234567``.
    """
    phone_number = phone_number.strip()

    try:
        ph_no = p.parse(phone_number)
    except p.NumberParseException as exc:
        printer.error(f"Could not parse phone number: {exc}")
        printer.info(
            "Make sure to include the country code, e.g. "
            f"{Style.BRIGHT}+358501234567{Style.RESET_ALL}"
        )
        return

    if not p.is_valid_number(ph_no):
        printer.warning(
            "The number does not appear to be valid. Results may be inaccurate."
        )

    _print_number_info(ph_no)
    _run_ignorant(ph_no)


# Internal helpers


def _print_number_info(ph_no: p.PhoneNumber) -> None:
    """
    Prints a structured breakdown of the parsed phone number.

    :param ph_no: Parsed :class:`phonenumbers.PhoneNumber` object.
    """
    e164 = p.format_number(ph_no, p.PhoneNumberFormat.E164)
    intl = p.format_number(ph_no, p.PhoneNumberFormat.INTERNATIONAL)
    national = p.format_number(ph_no, p.PhoneNumberFormat.NATIONAL)

    country = p.region_code_for_country_code(ph_no.country_code or 0)
    no_carrier = carrier.name_for_number(ph_no, "en")
    no_valid = p.is_valid_number(ph_no)
    no_possible = p.is_possible_number(ph_no)
    time_zones = timezone.time_zones_for_number(ph_no)
    region = geocoder.description_for_number(ph_no, "en")
    n_type = _NUMBER_TYPE_LABELS.get(int(number_type(ph_no)), "Unknown")

    printer.info(f"Looking up {Style.BRIGHT}{intl}{Style.RESET_ALL}...")
    time.sleep(0.5)

    printer.noprefix("")
    printer.section("Phone Number Details")
    printer.success(f"E.164 Format     : {Style.BRIGHT}{e164}{Style.RESET_ALL}")
    printer.success(f"International    : {intl}")
    printer.success(f"National         : {national}")
    printer.success(f"Country Code     : +{ph_no.country_code}")
    printer.success(f"Country          : {country or 'Unknown'}")
    printer.success(f"Region           : {region or 'Unknown'}")
    printer.success(f"Number Type      : {n_type}")
    printer.success(f"Carrier          : {no_carrier or 'Unknown'}")
    printer.success(f"Valid            : {no_valid}")
    printer.success(f"Possible         : {no_possible}")
    printer.success(
        "Time Zone(s)     : " + (", ".join(time_zones) if time_zones else "Unknown")
    )


def _run_ignorant(ph_no: p.PhoneNumber) -> None:
    """
    Runs *ignorant* against the phone number and prints social-media results.

    ``ignorant`` expects the country code and the national significant number
    as two separate positional arguments, e.g.::

        ignorant +1 3455685544

    We derive both values directly from the already-parsed
    :class:`~phonenumbers.PhoneNumber` object so no extra string manipulation
    is needed.

    :param ph_no: Parsed :class:`phonenumbers.PhoneNumber` object.
    """
    printer.noprefix("")
    printer.section("Social Media Presence (via ignorant)")

    country_code_arg = f"+{ph_no.country_code}"
    national_number_arg = str(ph_no.national_number)

    try:
        result = subprocess.run(
            [
                "ignorant",
                "--only-used",  # show only platforms where number IS registered
                "--no-color",  # plain text output for reliable parsing
                "--no-clear",  # do not wipe the terminal
                country_code_arg,
                national_number_arg,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        combined = result.stdout + result.stderr

        if not combined.strip():
            printer.warning("ignorant returned no output.")
            return

        found = _parse_ignorant_output(combined)

        if not found:
            printer.warning("No social media platforms found for this number.")
        else:
            printer.info(f"Found on {len(found)} platform(s):")
            for site in found:
                printer.success(f"  [+] {site}")

        printer.info("Credits to megadose (Palenath) for ignorant.")

    except FileNotFoundError:
        printer.error(
            f"{Style.BRIGHT}ignorant{Style.RESET_ALL} was not found. "
            f"Install it with: {Style.BRIGHT}pip install ignorant{Style.RESET_ALL}"
        )
    except subprocess.TimeoutExpired:
        printer.error("ignorant timed out. The request took too long.")
    except subprocess.CalledProcessError as exc:
        printer.error(f"ignorant exited with a non-zero status: {exc}")
    except Exception as exc:
        printer.error(f"Unexpected error while running ignorant: {exc}")


def _parse_ignorant_output(output: str) -> list[str]:
    """
    Extracts platform names from ignorant's ``[+] platform.com`` output lines.

    ignorant uses the same ``[+] / [-] / [x]`` convention as holehe.  Because
    we always pass ``--only-used``, only ``[+]`` lines appear in the output,
    but we guard against all three variants just in case.

    :param output: Raw stdout (and stderr) captured from the ignorant process.
    :return: Sorted list of platform names/domains that reported a match.
    """
    # Strip any residual ANSI escape codes that might slip through.
    ansi_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    found: list[str] = []

    for line in output.splitlines():
        clean = ansi_re.sub("", line).strip()
        # Capture the first token (domain) separately from the rest of the line.
        # ignorant prints a legend line at the bottom:
        #   [+] Phone number used, [-] Phone number not used, [x] Rate limit
        # Real platform domains (snapchat.com, instagram.com) always contain a
        # dot; the legend word "Phone" does not, so we use that to skip it.
        match = re.match(r"^\[(\+)\]\s*(\S+)", clean)
        if match:
            domain = match.group(2).strip()
            if "." not in domain:
                continue
            found.append(domain)

    return sorted(found)
