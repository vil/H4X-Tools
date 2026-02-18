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
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import phonenumbers
from colorama import Style
from ensta import Guest
from ensta.lib.Exceptions import APIError, NetworkError, RateLimitedError
from toutatis.core import advanced_lookup, getInfo

from helper import printer, timer

_KEY_WIDTH = 24
_SAVE_DIR = Path("scraped_data")


@dataclass
class Post:
    """A single Instagram post."""

    index: int = 0
    url: str = ""
    caption: str = ""


@dataclass
class IGProfile:
    """Aggregated Instagram profile data from all available sources."""

    # Basic identity
    username: str = ""
    user_id: str = ""
    full_name: str = ""
    biography: str = ""
    website: str = ""
    profile_pic_url: str = ""

    # Counts
    followers: int | str = "N/A"
    following: int | str = "N/A"
    posts: int | str = "N/A"
    igtv_videos: int | str = "N/A"

    # Status flags
    is_private: bool | str = "N/A"
    is_verified: bool | str = "N/A"
    is_business: bool | str = "N/A"
    is_whatsapp_linked: bool | str = "N/A"
    is_memorialized: bool | str = "N/A"
    is_new_to_instagram: bool | str = "N/A"

    # Contact — populated by toutatis when available
    public_email: str = ""
    public_phone: str = ""
    obfuscated_email: str = ""
    obfuscated_phone: str = ""

    # Recent posts — populated by ensta guest track
    recent_posts: list[Post] = field(default_factory=list)

    # Meta
    session_used: bool = False
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())


def _fetch_guest(username: str, profile: IGProfile) -> None:
    """
    Populate *profile* using the ensta Guest API (no authentication needed).

    Fills basic profile fields and recent posts.

    :param username: Instagram username to look up.
    :param profile:  :class:`IGProfile` to populate in-place.
    """
    try:
        api = Guest()
        data = api.profile(username)
        if data is None or not hasattr(data, "raw") or data.raw is None:
            printer.error("Ensta returned no data for this account.")
            return
        raw: dict = data.raw

        profile.username = raw.get("username", username)
        profile.user_id = str(raw.get("id", ""))
        profile.full_name = raw.get("full_name", "")
        profile.biography = raw.get("biography", "")
        profile.website = raw.get("external_url", "")
        profile.profile_pic_url = raw.get("profile_pic_url_hd", "")
        profile.followers = raw.get("edge_followed_by", {}).get("count", "N/A")
        profile.following = raw.get("edge_follow", {}).get("count", "N/A")
        profile.posts = raw.get("edge_owner_to_timeline_media", {}).get("count", "N/A")
        profile.is_private = raw.get("is_private", "N/A")
        profile.is_verified = raw.get("is_verified", "N/A")

        # Recent posts
        edges = raw.get("edge_owner_to_timeline_media", {}).get("edges", [])
        for idx, edge in enumerate(edges, start=1):
            node = edge.get("node", {})
            shortcode = node.get("shortcode", "")
            caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
            caption = caption_edges[0]["node"]["text"] if caption_edges else ""
            profile.recent_posts.append(
                Post(
                    index=idx,
                    url=(
                        f"https://www.instagram.com/p/{shortcode}/" if shortcode else ""
                    ),
                    caption=caption,
                )
            )

    except NetworkError as exc:
        printer.error(f"Network error during guest fetch: {exc}")
    except RateLimitedError:
        printer.error("Ensta rate limited. Try again later or provide a session ID.")
    except APIError as exc:
        printer.error(f"Ensta API error: {exc}")
    except AttributeError:
        printer.error(
            "Ensta returned no data. The account may not exist, be private, "
            "or Instagram may be blocking requests. Try providing a session ID."
        )


def _fetch_authenticated(username: str, session_id: str, profile: IGProfile) -> None:
    """
    Populate *profile* using the Toutatis authenticated API.

    Fills all basic fields plus business flag, WhatsApp/memorial/new-user
    flags, IGTV count, and public contact details (email / phone).

    :param username:   Instagram username.
    :param session_id: Instagram ``sessionid`` cookie value.
    :param profile:    :class:`IGProfile` to populate in-place.
    """
    result = getInfo(username, session_id)

    if result.get("error"):
        printer.error(f"Toutatis getInfo error: {result['error']}")
        printer.warning("Falling back to guest track for basic profile data.")
        _fetch_guest(username, profile)
        return

    info: dict = result.get("user", {})
    profile.session_used = True

    profile.username = info.get("username", username)
    profile.user_id = str(info.get("userID", info.get("pk", "")))
    profile.full_name = info.get("full_name", "")
    profile.biography = info.get("biography", "")
    profile.website = info.get("external_url", "")

    pic_info = info.get("hd_profile_pic_url_info") or {}
    profile.profile_pic_url = pic_info.get("url", info.get("profile_pic_url", ""))

    profile.followers = info.get("follower_count", "N/A")
    profile.following = info.get("following_count", "N/A")
    profile.posts = info.get("media_count", "N/A")
    profile.igtv_videos = info.get("total_igtv_videos", "N/A")

    profile.is_private = info.get("is_private", "N/A")
    profile.is_verified = info.get("is_verified", "N/A")
    profile.is_business = info.get("is_business", "N/A")
    profile.is_whatsapp_linked = info.get("is_whatsapp_linked", "N/A")
    profile.is_memorialized = info.get("is_memorialized", "N/A")
    profile.is_new_to_instagram = info.get("is_new_to_instagram", "N/A")

    # Public email
    if info.get("public_email"):
        profile.public_email = info["public_email"]

    # Public phone — format with phonenumbers library if possible
    raw_phone = str(info.get("public_phone_number", "")).strip()
    country_code = str(info.get("public_phone_country_code", "")).strip()
    if raw_phone and raw_phone not in {"0", ""}:
        full = f"+{country_code} {raw_phone}" if country_code else raw_phone
        try:
            pn = phonenumbers.parse(full)
            profile.public_phone = phonenumbers.format_number(
                pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except phonenumbers.NumberParseException:
            profile.public_phone = full


def _fetch_advanced_lookup(username: str, profile: IGProfile) -> None:
    """
    Run the Toutatis ``advanced_lookup`` to surface obfuscated contact info.

    This endpoint uses Instagram's account-recovery flow and requires no
    session cookie, but may be rate-limited.

    :param username: Instagram username.
    :param profile:  :class:`IGProfile` to populate in-place.
    """
    printer.info("Running Toutatis advanced lookup (obfuscated contact)...")
    result = advanced_lookup(username)

    if result.get("error") == "rate limit":
        printer.warning(
            "Advanced lookup rate limited. Obfuscated contact info unavailable."
        )
        return

    user_data: dict = result.get("user") or {}

    if user_data.get("message") == "No users found":
        printer.warning("Advanced lookup: no users found for this username.")
        return

    msg = user_data.get("message")
    if msg:
        printer.debug(f"Advanced lookup message: {msg}")

    obf_email = user_data.get("obfuscated_email", "")
    obf_phone = str(user_data.get("obfuscated_phone", "")).strip()

    if obf_email:
        profile.obfuscated_email = obf_email
    if obf_phone and obf_phone not in {"None", "0", ""}:
        profile.obfuscated_phone = obf_phone


def _print_profile(profile: IGProfile) -> None:
    """Render the full :class:`IGProfile` to the terminal."""
    printer.noprefix("")
    printer.section("Instagram Profile")

    rows = [
        ("Username", profile.username),
        ("User ID", profile.user_id),
        ("Full Name", profile.full_name),
        ("Biography", profile.biography),
        ("Website", profile.website),
        ("Followers", profile.followers),
        ("Following", profile.following),
        ("Total Posts", profile.posts),
        ("IGTV Videos", profile.igtv_videos),
        ("Private", profile.is_private),
        ("Verified", profile.is_verified),
        ("Business Account", profile.is_business),
        ("WhatsApp Linked", profile.is_whatsapp_linked),
        ("Memorial Account", profile.is_memorialized),
        ("New User", profile.is_new_to_instagram),
        ("Profile Picture", profile.profile_pic_url),
    ]
    for label, value in rows:
        if value not in ("", "N/A", False, None):
            printer.success(f"{label:<{_KEY_WIDTH}} : {value}")
        elif value == "N/A":
            printer.success(f"{label:<{_KEY_WIDTH}} : N/A")

    # Contact section
    has_contact = any(
        [
            profile.public_email,
            profile.public_phone,
            profile.obfuscated_email,
            profile.obfuscated_phone,
        ]
    )
    if has_contact:
        printer.noprefix("")
        printer.section("Contact Information")
        if profile.public_email:
            printer.success(f"{'Public Email':<{_KEY_WIDTH}} : {profile.public_email}")
        if profile.public_phone:
            printer.success(f"{'Public Phone':<{_KEY_WIDTH}} : {profile.public_phone}")
        if profile.obfuscated_email:
            printer.success(
                f"{'Obfuscated Email':<{_KEY_WIDTH}} : {profile.obfuscated_email}"
            )
        if profile.obfuscated_phone:
            printer.success(
                f"{'Obfuscated Phone':<{_KEY_WIDTH}} : {profile.obfuscated_phone}"
            )

    # Recent posts (guest track only)
    if profile.recent_posts:
        printer.noprefix("")
        printer.section("Recent Posts")
        for post in profile.recent_posts:
            printer.success(f"Post {post.index}")
            if post.url:
                printer.success(f"  {'URL':<{_KEY_WIDTH - 2}} : {post.url}")
            if post.caption:
                cap = (
                    post.caption
                    if len(post.caption) <= 120
                    else post.caption[:117] + "..."
                )
                printer.success(f"  {'Caption':<{_KEY_WIDTH - 2}} : {cap}")
            printer.noprefix("")
    elif not profile.session_used:
        printer.warning("No recent posts found (account may be private).")

    printer.noprefix("")
    source = (
        "Toutatis + ensta  (authenticated)"
        if profile.session_used
        else "ensta guest + Toutatis advanced lookup"
    )
    printer.info(f"{'Data source':<{_KEY_WIDTH}} : {source}")
    printer.info(f"{'Scraped at':<{_KEY_WIDTH}} : {profile.scraped_at}")


def _ask_export() -> str | None:
    """
    Prompt the user for an optional export format.

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


def _export(profile: IGProfile, fmt: str) -> None:
    """
    Write *profile* to ``scraped_data/`` in the requested format.

    :param profile: The populated :class:`IGProfile` to export.
    :param fmt:     ``'txt'``, ``'csv'``, or ``'json'``.
    """
    _SAVE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = profile.username or "unknown"

    try:
        match fmt.lower():
            case "txt":
                filepath = _SAVE_DIR / f"igscrape_{slug}_{timestamp}.txt"
                with filepath.open("w", encoding="utf-8") as fh:
                    fh.write("Instagram Scrape Report\n")
                    fh.write(f"Target     : {profile.username}\n")
                    fh.write(
                        f"Date       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    fh.write(
                        f"Auth       : {'Yes (session)' if profile.session_used else 'No (guest)'}\n"
                    )
                    fh.write("=" * 80 + "\n\n")

                    fh.write("PROFILE\n" + "-" * 40 + "\n")
                    fields = [
                        ("Username", profile.username),
                        ("User ID", profile.user_id),
                        ("Full Name", profile.full_name),
                        ("Biography", profile.biography),
                        ("Website", profile.website),
                        ("Followers", profile.followers),
                        ("Following", profile.following),
                        ("Total Posts", profile.posts),
                        ("IGTV Videos", profile.igtv_videos),
                        ("Private", profile.is_private),
                        ("Verified", profile.is_verified),
                        ("Business", profile.is_business),
                        ("WhatsApp Linked", profile.is_whatsapp_linked),
                        ("Memorial", profile.is_memorialized),
                        ("New User", profile.is_new_to_instagram),
                        ("Profile Pic", profile.profile_pic_url),
                    ]
                    for label, val in fields:
                        fh.write(f"  {label:<22}: {val}\n")

                    fh.write("\nCONTACT\n" + "-" * 40 + "\n")
                    fh.write(f"  Public Email    : {profile.public_email or 'N/A'}\n")
                    fh.write(f"  Public Phone    : {profile.public_phone or 'N/A'}\n")
                    fh.write(
                        f"  Obfusc. Email   : {profile.obfuscated_email or 'N/A'}\n"
                    )
                    fh.write(
                        f"  Obfusc. Phone   : {profile.obfuscated_phone or 'N/A'}\n"
                    )

                    if profile.recent_posts:
                        fh.write("\nRECENT POSTS\n" + "-" * 40 + "\n")
                        for post in profile.recent_posts:
                            fh.write(f"  [{post.index}] {post.url}\n")
                            if post.caption:
                                fh.write(f"      {post.caption}\n")
                            fh.write("\n")

                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "csv":
                filepath = _SAVE_DIR / f"igscrape_{slug}_{timestamp}.csv"
                with filepath.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    # Profile sheet
                    writer.writerow(["field", "value"])
                    for label, val in [
                        ("username", profile.username),
                        ("user_id", profile.user_id),
                        ("full_name", profile.full_name),
                        ("biography", profile.biography),
                        ("website", profile.website),
                        ("followers", profile.followers),
                        ("following", profile.following),
                        ("posts", profile.posts),
                        ("igtv_videos", profile.igtv_videos),
                        ("is_private", profile.is_private),
                        ("is_verified", profile.is_verified),
                        ("is_business", profile.is_business),
                        ("is_whatsapp_linked", profile.is_whatsapp_linked),
                        ("is_memorialized", profile.is_memorialized),
                        ("is_new_to_instagram", profile.is_new_to_instagram),
                        ("profile_pic_url", profile.profile_pic_url),
                        ("public_email", profile.public_email),
                        ("public_phone", profile.public_phone),
                        ("obfuscated_email", profile.obfuscated_email),
                        ("obfuscated_phone", profile.obfuscated_phone),
                        ("session_used", profile.session_used),
                        ("scraped_at", profile.scraped_at),
                    ]:
                        writer.writerow([label, val])

                    if profile.recent_posts:
                        writer.writerow([])
                        writer.writerow(["post_index", "post_url", "caption"])
                        for post in profile.recent_posts:
                            writer.writerow([post.index, post.url, post.caption])

                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case "json":
                filepath = _SAVE_DIR / f"igscrape_{slug}_{timestamp}.json"
                payload = asdict(profile)
                # recent_posts are dataclasses too — asdict handles them
                with filepath.open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)
                printer.success(
                    f"Results saved → {Style.BRIGHT}{filepath}{Style.RESET_ALL}"
                )

            case _:
                printer.error(f"Unknown format '{fmt}'. Use 'txt', 'csv', or 'json'.")

    except OSError as exc:
        printer.error(f"Could not write file: {exc}")


@timer.timer(require_input=True)
def scrape(target: str) -> None:
    """
    Scrapes and aggregates data from an Instagram account.

    Two tracks are supported:

    **Guest track** (no session ID)
      Uses the ``ensta`` Guest API for public profile data and recent posts,
      then runs the Toutatis ``advanced_lookup`` to surface any obfuscated
      e-mail address or phone number tied to the account's recovery flow.

    **Authenticated track** (session ID provided)
      Uses Toutatis ``getInfo()`` via Instagram's private mobile API for a
      richer profile including business flags, IGTV count, WhatsApp link
      status, and publicly listed contact details, then also runs
      ``advanced_lookup`` for the obfuscated recovery contacts.

    The session ID is your Instagram ``sessionid`` cookie value.  To find it:
    open Instagram in a browser → DevTools → Application → Cookies →
    copy the value of the ``sessionid`` cookie.

    Results can be exported to ``scraped_data/`` as TXT, CSV, or JSON.

    :param target: The Instagram username to investigate.
    """
    target = target.strip().lstrip("@")
    if not target:
        printer.error("Username cannot be empty.")
        return

    printer.noprefix("")
    printer.info(
        "Provide your Instagram session ID for richer data (phone, email, "
        "business flags, etc.)."
    )
    printer.info(
        "Find it in your browser: DevTools → Application → Cookies → sessionid"
    )
    session_id = printer.user_input(
        "Session ID (leave blank for guest mode) : "
    ).strip()

    profile = IGProfile()

    if session_id:
        printer.info(
            f"Authenticated scrape for {Style.BRIGHT}{target}{Style.RESET_ALL}..."
        )
        _fetch_authenticated(target, session_id, profile)
    else:
        printer.info(
            f"Guest scrape for {Style.BRIGHT}{target}{Style.RESET_ALL} "
            "(no session ID — limited data)..."
        )
        _fetch_guest(target, profile)

    # Advanced lookup runs regardless of authentication track.
    _fetch_advanced_lookup(target, profile)

    if not profile.username:
        printer.error("No data could be retrieved for this account.")
        return

    _print_profile(profile)

    printer.noprefix("")
    fmt = _ask_export()
    if fmt:
        _export(profile, fmt)
