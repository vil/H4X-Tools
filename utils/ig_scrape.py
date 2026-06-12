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
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import phonenumbers
import requests
from colorama import Style
from ensta import Guest
from ensta.lib.Exceptions import APIError, NetworkError, RateLimitedError

from helper import config, printer, timer

_KEY_WIDTH = 24
_SAVE_DIR = Path("scraped_data")
_CONFIG_SECTION = "ig_scrape"
_SESSION_ID_KEY = "session_id"
_WEB_IG_APP_ID = "936619743392459"
_RECOVERY_GRAPHQL_DOC_ID = "35299094813070532"
_RECOVERY_GRAPHQL_FRIENDLY_NAME = "CAAIGAccountSearchViewQuery"
_WEB_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)
_MOBILE_UA = (
    "Instagram 320.0.0.0.0 Android (29/10; 300dpi; 1080x1920; "
    "samsung; SM-G981B; y2s; exynos990; en_US; 314660352)"
)


@dataclass
class RecoveryContactPoint:
    """An obfuscated account-recovery contact point returned by Instagram."""

    index: int = 0
    contact_point: str = ""
    title: str = ""
    type: str = ""


@dataclass
class MediaItem:
    """A downloadable media object attached to a post, story, or reel."""

    index: int = 0
    media_type: str = "unknown"
    url: str = ""
    accessibility_caption: str = ""


@dataclass
class Comment:
    """A single Instagram post comment."""

    index: int = 0
    id: str = ""
    pk: str = ""
    username: str = ""
    user_id: str = ""
    full_name: str = ""
    text: str = ""
    created_at: int | str = ""
    like_count: int | str = "N/A"


@dataclass
class Post:
    """A single Instagram post with lightweight OSINT metadata."""

    index: int = 0
    id: str = ""
    pk: str = ""
    shortcode: str = ""
    url: str = ""
    caption: str = ""
    taken_at: int | str = ""
    media_type: str = "unknown"
    is_video: bool = False
    like_count: int | str = "N/A"
    comment_count: int | str = "N/A"
    accessibility_caption: str = ""
    display_url: str = ""
    video_url: str = ""
    mentions: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    tagged_users: list[str] = field(default_factory=list)
    media_items: list[MediaItem] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)


@dataclass
class StoryItem:
    """An active story or saved highlight item."""

    index: int = 0
    id: str = ""
    pk: str = ""
    code: str = ""
    url: str = ""
    taken_at: int | str = ""
    media_type: str = "unknown"
    is_video: bool = False
    is_highlight: bool = False
    highlight_title: str = ""
    accessibility_caption: str = ""
    mentions: list[str] = field(default_factory=list)


@dataclass
class ReelItem:
    """A profile reel / clip item."""

    index: int = 0
    id: str = ""
    pk: str = ""
    code: str = ""
    url: str = ""
    caption: str = ""
    taken_at: int | str = ""
    play_count: int | str = "N/A"
    like_count: int | str = "N/A"
    comment_count: int | str = "N/A"
    video_url: str = ""
    cover_url: str = ""
    mentions: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)


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

    # Contact — populated by authenticated Instagram endpoints when available
    public_email: str = ""
    public_phone: str = ""
    obfuscated_email: str = ""
    obfuscated_phone: str = ""
    recovery_contact_points: list[RecoveryContactPoint] = field(default_factory=list)

    # Content
    recent_posts: list[Post] = field(default_factory=list)
    stories: list[StoryItem] = field(default_factory=list)
    highlights: list[StoryItem] = field(default_factory=list)
    reels: list[ReelItem] = field(default_factory=list)

    # Meta
    session_used: bool = False
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())


def _parse_text_intel(text: str) -> tuple[list[str], list[str]]:
    """Extract unique @mentions and #hashtags from text."""
    if not text:
        return [], []
    mentions = sorted({m.lower() for m in re.findall(r"@([A-Za-z0-9_.]+)", text)})
    hashtags = sorted({h.lower() for h in re.findall(r"#([A-Za-z0-9_]+)", text)})
    return mentions, hashtags


def _media_kind(media_type: int | str | None) -> str:
    """Normalize Instagram media type values to a readable label."""
    if media_type in {1, "1", "GraphImage"}:
        return "image"
    if media_type in {2, "2", "GraphVideo"}:
        return "video"
    if media_type in {8, "8", "GraphSidecar"}:
        return "carousel"
    return str(media_type or "unknown")


def _first_candidate_url(node: dict) -> str:
    """Return the best image URL from the common Instagram response shapes."""
    if node.get("display_url"):
        return node["display_url"]
    candidates = (node.get("image_versions2") or {}).get("candidates") or []
    if candidates:
        return candidates[0].get("url", "")
    if node.get("thumbnail_url"):
        return node["thumbnail_url"]
    return ""


def _first_video_url(node: dict) -> str:
    """Return the first video URL from the common Instagram response shapes."""
    if node.get("video_url"):
        return node["video_url"]
    versions = node.get("video_versions") or []
    if versions:
        return versions[0].get("url", "")
    return ""


def _caption_text(node: dict) -> str:
    """Extract caption text from web GraphQL or mobile API item shapes."""
    caption = node.get("caption")
    if isinstance(caption, dict):
        return caption.get("text", "") or ""
    if isinstance(caption, str):
        return caption

    caption_edges = (node.get("edge_media_to_caption") or {}).get("edges") or []
    if caption_edges:
        return (caption_edges[0].get("node") or {}).get("text") or ""
    return ""


def _tagged_users(node: dict) -> list[str]:
    """Extract users tagged in media from web GraphQL or mobile API item shapes."""
    users: set[str] = set()
    for tag in (node.get("usertags") or {}).get("in", []) or []:
        username = (tag.get("user") or {}).get("username")
        if username:
            users.add(username)
    for edge in (node.get("edge_media_to_tagged_user") or {}).get("edges") or []:
        username = ((edge.get("node") or {}).get("user") or {}).get("username")
        if username:
            users.add(username)
    return sorted(users)


def _normalize_media_item(node: dict, index: int) -> MediaItem:
    """Normalize a single media object to :class:`MediaItem`."""
    media_type = node.get("media_type", node.get("__typename"))
    kind = _media_kind(media_type)
    return MediaItem(
        index=index,
        media_type=kind,
        url=_first_video_url(node) if kind == "video" else _first_candidate_url(node),
        accessibility_caption=node.get("accessibility_caption", "") or "",
    )


def _normalize_comment(node: dict, index: int) -> Comment:
    """Normalize an Instagram comment object."""
    user = node.get("user") or {}
    return Comment(
        index=index,
        id=str(node.get("id", "") or ""),
        pk=str(node.get("pk", "") or ""),
        username=user.get("username", "") or "",
        user_id=str(user.get("pk", user.get("id", "")) or ""),
        full_name=user.get("full_name", "") or "",
        text=node.get("text", "") or "",
        created_at=node.get("created_at", "") or "",
        like_count=node.get("comment_like_count", node.get("like_count", "N/A")),
    )


def _normalize_post(node: dict, index: int) -> Post:
    """Normalize a web/mobile Instagram post node to :class:`Post`."""
    caption = _caption_text(node)
    mentions, hashtags = _parse_text_intel(caption)
    media_type = node.get("media_type", node.get("__typename"))
    kind = _media_kind(media_type)
    shortcode = node.get("shortcode", node.get("code", "")) or ""
    is_video = kind == "video" or bool(node.get("is_video"))
    like_count = node.get("like_count")
    if like_count is None:
        like_count = (node.get("edge_liked_by") or {}).get("count", "N/A")
    comment_count = node.get("comment_count")
    if comment_count is None:
        comment_count = (node.get("edge_media_to_comment") or {}).get("count", "N/A")

    media_items: list[MediaItem] = []
    carousel = node.get("carousel_media") or []
    if carousel:
        media_items = [
            _normalize_media_item(item, idx) for idx, item in enumerate(carousel, 1)
        ]
    else:
        sidecar_edges = (node.get("edge_sidecar_to_children") or {}).get("edges") or []
        if sidecar_edges:
            media_items = [
                _normalize_media_item(edge.get("node") or {}, idx)
                for idx, edge in enumerate(sidecar_edges, 1)
            ]

    if not media_items:
        media_items.append(_normalize_media_item(node, 1))

    return Post(
        index=index,
        id=str(node.get("id", "") or ""),
        pk=str(node.get("pk", node.get("id", "")) or ""),
        shortcode=shortcode,
        url=f"https://www.instagram.com/p/{shortcode}/" if shortcode else "",
        caption=caption,
        taken_at=node.get("taken_at", node.get("taken_at_timestamp", "")) or "",
        media_type=kind,
        is_video=is_video,
        like_count=like_count,
        comment_count=comment_count,
        accessibility_caption=node.get("accessibility_caption", "") or "",
        display_url=_first_candidate_url(node),
        video_url=_first_video_url(node),
        mentions=mentions,
        hashtags=hashtags,
        tagged_users=_tagged_users(node),
        media_items=[item for item in media_items if item.url],
    )


def _normalize_story_item(
    item: dict,
    index: int,
    *,
    is_highlight: bool = False,
    highlight_title: str = "",
) -> StoryItem:
    """Normalize an active story or highlight item."""
    kind = _media_kind(item.get("media_type"))
    is_video = kind == "video"
    mentions = []
    for mention in item.get("reel_mentions", []) or []:
        username = (mention.get("user") or {}).get("username")
        if username:
            mentions.append(username)
    media_url = _first_video_url(item) if is_video else _first_candidate_url(item)
    return StoryItem(
        index=index,
        id=str(item.get("id", "") or ""),
        pk=str(item.get("pk", "") or ""),
        code=item.get("code", "") or "",
        url=media_url,
        taken_at=item.get("taken_at", "") or "",
        media_type=kind,
        is_video=is_video,
        is_highlight=is_highlight,
        highlight_title=highlight_title,
        accessibility_caption=item.get("accessibility_caption", "") or "",
        mentions=sorted(set(mentions)),
    )


def _normalize_reel(item: dict, index: int) -> ReelItem:
    """Normalize an Instagram clips/reels item."""
    raw_media = item.get("media")
    media: dict = raw_media if isinstance(raw_media, dict) else item
    caption = _caption_text(media)
    mentions, hashtags = _parse_text_intel(caption)
    code = media.get("code", media.get("shortcode", "")) or ""
    return ReelItem(
        index=index,
        id=str(media.get("id", "") or ""),
        pk=str(media.get("pk", "") or ""),
        code=code,
        url=f"https://www.instagram.com/reel/{code}/" if code else "",
        caption=caption,
        taken_at=media.get("taken_at", "") or "",
        play_count=media.get("play_count", media.get("ig_play_count", "N/A")),
        like_count=media.get("like_count", "N/A"),
        comment_count=media.get("comment_count", "N/A"),
        video_url=_first_video_url(media),
        cover_url=_first_candidate_url(media),
        mentions=mentions,
        hashtags=hashtags,
    )


def _mobile_headers() -> dict[str, str]:
    """Headers that work better with Instagram's mobile/private API endpoints."""
    return {
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "User-Agent": _MOBILE_UA,
        "X-IG-App-ID": _WEB_IG_APP_ID,
    }


def _web_headers() -> dict[str, str]:
    """Headers for Instagram web endpoints that also work in guest mode."""
    return {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.instagram.com",
        "Referer": "https://www.instagram.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": _WEB_UA,
        "X-IG-App-ID": _WEB_IG_APP_ID,
    }


def _session_cookies(session_id: str) -> dict[str, str]:
    """Build a minimal Instagram cookie jar from a session ID."""
    return {"sessionid": session_id} if session_id else {}


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

        # Recent public posts exposed by the guest profile payload.
        edges = raw.get("edge_owner_to_timeline_media", {}).get("edges", [])
        for idx, edge in enumerate(edges, start=1):
            node = edge.get("node", {})
            if node:
                profile.recent_posts.append(_normalize_post(node, idx))

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


def _get_instagram_user_id(username: str, session_id: str) -> dict:
    """
    Resolve an Instagram username to a numeric user ID.

    Uses the same Instagram endpoint as the old external helper, but keeps the
    implementation local so H4X-Tools controls error handling.

    :param username: Instagram username.
    :param session_id: Instagram ``sessionid`` cookie value.
    :return: ``{"id": str | None, "error": str | None}``.
    """
    try:
        response = requests.get(
            "https://i.instagram.com/api/v1/users/web_profile_info/",
            params={"username": username},
            headers={"User-Agent": _WEB_UA, "x-ig-app-id": _WEB_IG_APP_ID},
            cookies={"sessionid": session_id},
            timeout=20,
        )
    except requests.RequestException as exc:
        return {"id": None, "error": f"Network error: {exc}"}

    if response.status_code == 404:
        return {"id": None, "error": "User not found"}
    if response.status_code == 429:
        return {"id": None, "error": "Rate limit"}
    if response.status_code in {401, 403}:
        return {"id": None, "error": "Access denied; session ID may be invalid"}

    try:
        payload = response.json()
    except json.JSONDecodeError:
        return {"id": None, "error": "Rate limit or invalid Instagram response"}

    user_id = payload.get("data", {}).get("user", {}).get("id")
    if not user_id:
        return {"id": None, "error": "User not found"}

    return {"id": str(user_id), "error": None}


def _get_instagram_info(
    search: str,
    session_id: str,
    search_type: str = "username",
) -> dict:
    """
    Fetch Instagram private mobile API profile info.

    This local implementation uses defensive missing-key handling because
    Instagram frequently changes which fields are present.

    :param search: Username or numeric user ID.
    :param session_id: Instagram ``sessionid`` cookie value.
    :param search_type: ``"username"`` or ``"id"``.
    :return: ``{"user": dict | None, "error": str | None}``.
    """
    if search_type == "username":
        data = _get_instagram_user_id(search, session_id)
        if data["error"]:
            return data | {"user": None}
        user_id = data["id"]
    else:
        try:
            user_id = str(int(search))
        except ValueError:
            return {"user": None, "error": "Invalid ID"}

    try:
        response = requests.get(
            f"https://i.instagram.com/api/v1/users/{user_id}/info/",
            headers=_mobile_headers(),
            cookies={"sessionid": session_id},
            timeout=20,
        )
    except requests.RequestException:
        return {"user": None, "error": "Not found"}

    if response.status_code == 429:
        return {"user": None, "error": "Rate limit"}
    if response.status_code in {401, 403}:
        return {"user": None, "error": "Access denied; session ID may be invalid"}

    try:
        response.raise_for_status()
        info_user = response.json().get("user")
    except (requests.RequestException, json.JSONDecodeError):
        return {"user": None, "error": "Not found"}

    if not info_user:
        return {"user": None, "error": "Not found"}

    info_user["userID"] = user_id
    return {"user": info_user, "error": None}


def _fetch_post_comments(
    media_id: str,
    session_id: str,
    *,
    limit: int = 20,
) -> list[Comment]:
    """Fetch comments for a media/post ID using Instagram's web API."""
    if not media_id:
        return []

    url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
    params = {"can_support_threading": "true", "permalink_enabled": "false"}
    headers = _web_headers()
    headers["Referer"] = "https://www.instagram.com/"

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            cookies=_session_cookies(session_id),
            timeout=20,
        )
    except requests.RequestException as exc:
        printer.warning(f"Could not fetch comments for media {media_id}: {exc}")
        return []

    printer.verbose(
        f"Comments lookup for media {media_id}: HTTP {response.status_code} "
        f"({len(response.content)} bytes)"
    )
    printer.debug(f"Comments lookup raw response: {_response_snippet(response)}")

    if response.status_code in {401, 403}:
        printer.debug(f"Comments denied for media {media_id}.")
        return []
    if response.status_code == 429:
        printer.warning(f"Comments lookup rate limited for media {media_id}.")
        return []
    if response.status_code != 200:
        printer.debug(
            f"Comments lookup for media {media_id} returned HTTP {response.status_code}"
        )
        return []

    try:
        payload = response.json()
    except json.JSONDecodeError:
        printer.debug(f"Comments lookup for media {media_id} returned invalid JSON.")
        return []

    comments = payload.get("comments") or []
    normalized = [
        _normalize_comment(comment, idx)
        for idx, comment in enumerate(comments[:limit], 1)
        if isinstance(comment, dict)
    ]
    printer.verbose(
        f"Comments lookup for media {media_id}: extracted {len(normalized)} comment(s)."
    )
    return normalized


def _fetch_authenticated_posts(
    user_id: str, session_id: str, limit: int = 12, comments_limit: int = 20
) -> list[Post]:
    """Fetch recent timeline posts through Instagram's authenticated feed endpoint."""
    try:
        response = requests.get(
            f"https://i.instagram.com/api/v1/feed/user/{user_id}/",
            params={"count": limit},
            headers=_mobile_headers(),
            cookies=_session_cookies(session_id),
            timeout=20,
        )
    except requests.RequestException as exc:
        printer.warning(f"Could not fetch authenticated posts: {exc}")
        return []

    if response.status_code in {401, 403}:
        printer.warning("Post feed denied; session ID may be invalid or lacks access.")
        return []
    if response.status_code == 429:
        printer.warning("Post feed rate limited.")
        return []
    if response.status_code != 200:
        printer.debug(f"Post feed returned HTTP {response.status_code}")
        return []

    try:
        items = response.json().get("items") or []
    except json.JSONDecodeError:
        return []

    posts = [_normalize_post(item, idx) for idx, item in enumerate(items[:limit], 1)]
    posts = [post for post in posts if post.url or post.caption or post.media_items]

    for post in posts:
        if post.pk:
            if comments_limit and comments_limit > 0:
                post.comments = _fetch_post_comments(
                    post.pk, session_id, limit=comments_limit
                )
                time.sleep(0.35)
            else:
                post.comments = []

    return posts


def _fetch_authenticated_stories(user_id: str, session_id: str) -> list[StoryItem]:
    """Fetch currently active 24-hour stories for a user."""
    try:
        response = requests.get(
            "https://i.instagram.com/api/v1/feed/reels_media/",
            params={"reel_ids": user_id},
            headers=_mobile_headers(),
            cookies=_session_cookies(session_id),
            timeout=20,
        )
    except requests.RequestException as exc:
        printer.warning(f"Could not fetch active stories: {exc}")
        return []

    if response.status_code in {401, 403}:
        printer.debug("Active stories denied by Instagram.")
        return []
    if response.status_code == 429:
        printer.warning("Active stories endpoint rate limited.")
        return []
    if response.status_code != 200:
        printer.debug(f"Active stories returned HTTP {response.status_code}")
        return []

    try:
        payload = response.json()
    except json.JSONDecodeError:
        return []

    reels_media = payload.get("reels_media") or []
    if not reels_media and isinstance(payload.get("reels"), dict):
        reels_media = list(payload["reels"].values())

    stories: list[StoryItem] = []
    for reel in reels_media:
        for item in reel.get("items", []) or []:
            story = _normalize_story_item(item, len(stories) + 1)
            if story.url or story.code or story.pk:
                stories.append(story)
    return stories


def _fetch_authenticated_highlights(user_id: str, session_id: str) -> list[StoryItem]:
    """Fetch saved story highlights and their contained media."""
    try:
        tray_response = requests.get(
            f"https://i.instagram.com/api/v1/highlights/{user_id}/highlights_tray/",
            headers=_mobile_headers(),
            cookies=_session_cookies(session_id),
            timeout=20,
        )
    except requests.RequestException as exc:
        printer.warning(f"Could not fetch highlights tray: {exc}")
        return []

    if tray_response.status_code in {401, 403}:
        printer.debug("Highlights denied by Instagram.")
        return []
    if tray_response.status_code == 429:
        printer.warning("Highlights endpoint rate limited.")
        return []
    if tray_response.status_code != 200:
        printer.debug(f"Highlights tray returned HTTP {tray_response.status_code}")
        return []

    try:
        tray = tray_response.json().get("tray") or []
    except json.JSONDecodeError:
        return []

    highlights: list[StoryItem] = []
    for highlight in tray:
        highlight_id = highlight.get("id")
        if not highlight_id:
            continue
        try:
            media_response = requests.get(
                "https://i.instagram.com/api/v1/feed/reels_media/",
                params={"reel_ids": highlight_id},
                headers=_mobile_headers(),
                cookies=_session_cookies(session_id),
                timeout=20,
            )
        except requests.RequestException:
            continue

        if media_response.status_code != 200:
            continue
        try:
            media_payload = media_response.json()
        except json.JSONDecodeError:
            continue

        reels_media = media_payload.get("reels_media") or []
        if not reels_media and isinstance(media_payload.get("reels"), dict):
            reels_media = list(media_payload["reels"].values())

        for reel in reels_media:
            for item in reel.get("items", []) or []:
                story = _normalize_story_item(
                    item,
                    len(highlights) + 1,
                    is_highlight=True,
                    highlight_title=highlight.get("title", "") or "",
                )
                if story.url or story.code or story.pk:
                    highlights.append(story)
        time.sleep(0.5)

    return highlights


def _fetch_authenticated_reels(
    user_id: str, session_id: str, limit: int = 12
) -> list[ReelItem]:
    """Fetch profile reels/clips when Instagram allows the endpoint for the session."""
    endpoints = [
        "https://i.instagram.com/api/v1/clips/user/",
        "https://www.instagram.com/api/v1/clips/user/",
    ]
    for endpoint in endpoints:
        try:
            response = requests.get(
                endpoint,
                params={"target_user_id": user_id, "page_size": limit},
                headers=_mobile_headers(),
                cookies=_session_cookies(session_id),
                timeout=20,
            )
        except requests.RequestException:
            continue

        if response.status_code in {401, 403, 404}:
            continue
        if response.status_code == 429:
            printer.warning("Reels endpoint rate limited.")
            return []
        if response.status_code != 200:
            continue

        try:
            payload = response.json()
        except json.JSONDecodeError:
            continue

        items = payload.get("items") or payload.get("clips") or []
        reels = [
            _normalize_reel(item, idx) for idx, item in enumerate(items[:limit], 1)
        ]
        return [reel for reel in reels if reel.url or reel.caption or reel.video_url]

    printer.debug("Reels endpoint unavailable for this target/session.")
    return []


def _response_snippet(response: requests.Response, limit: int = 600) -> str:
    """Return a compact, newline-safe response body preview for debug logs."""
    text = response.text.replace("\r", " ").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _debug_lookup_response(label: str, response: requests.Response) -> None:
    """Emit verbose/debug diagnostics for Instagram recovery lookup responses."""
    content_type = response.headers.get("content-type", "unknown")
    printer.verbose(
        f"Advanced lookup [{label}] HTTP {response.status_code} "
        f"({content_type}, {len(response.content)} bytes)"
    )
    printer.debug(f"Advanced lookup [{label}] final URL: {response.url}")
    interesting_headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower()
        in {
            "ig-set-authorization",
            "ig-set-password-encryption-key-id",
            "ig-set-password-encryption-pub-key",
            "x-ig-set-www-claim",
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset",
        }
    }
    if interesting_headers:
        printer.debug(
            "Advanced lookup response headers: "
            + json.dumps(interesting_headers, ensure_ascii=False)
        )
    printer.debug(
        f"Advanced lookup [{label}] raw response: {_response_snippet(response)}"
    )


def _normalize_recovery_contact_point(node: dict, index: int) -> RecoveryContactPoint:
    """Normalize a recovery contact point returned by the web account search query."""
    return RecoveryContactPoint(
        index=int(node.get("index", index) or index),
        contact_point=node.get("contact_point", "") or "",
        title=node.get("title", "") or "",
        type=str(node.get("type", "") or "").upper(),
    )


def _jazoest(seed: str) -> str:
    """Build the jazoest value commonly paired with Instagram web LSD tokens."""
    return "2" + "".join(str(ord(char)) for char in seed)


def _extract_lsd(html: str) -> str:
    """Extract Instagram's web LSD token from a bootstrap HTML response."""
    patterns = [
        r'"LSD",\s*\[\],\s*\{"token":"([^"]+)"\}',
        r'"lsd":"([^"]+)"',
        r'name="lsd"\s+value="([^"]+)"',
        r'"LSD".*?"token":"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return ""


def _fetch_web_recovery_context() -> tuple[
    requests.Session, str, str, list[dict[str, object]]
]:
    """Fetch fresh guest browser cookies and tokens for Instagram web GraphQL."""
    session = requests.Session()
    session.headers.update(_web_headers())
    attempts: list[dict[str, object]] = []

    for url in (
        "https://www.instagram.com/accounts/password/reset/",
        "https://www.instagram.com/",
    ):
        try:
            response = session.get(url, timeout=20)
        except requests.RequestException as exc:
            attempts.append({"label": "web_context", "url": url, "error": str(exc)})
            continue

        attempts.append(
            {
                "label": "web_context",
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
            }
        )
        printer.verbose(
            f"Advanced lookup [web_context] GET {url}: HTTP {response.status_code} "
            f"({len(response.content)} bytes)"
        )
        printer.debug(
            f"Advanced lookup [web_context] body: {_response_snippet(response)}"
        )

        if response.status_code != 200:
            continue

        lsd = _extract_lsd(response.text)
        csrf = session.cookies.get("csrftoken", "")
        if lsd and csrf:
            printer.verbose(
                "Advanced lookup [web_context] acquired fresh lsd/csrftoken."
            )
            return session, lsd, csrf, attempts

        attempts[-1]["lsd_found"] = bool(lsd)
        attempts[-1]["csrf_found"] = bool(csrf)

    return session, "", session.cookies.get("csrftoken") or "", attempts


def _instagram_graphql_recovery_lookup(username: str) -> dict:
    """Use Instagram web's forgot-password GraphQL account search query."""
    session, lsd, csrf, attempts = _fetch_web_recovery_context()
    label = "web_graphql_account_search"

    if not lsd or not csrf:
        attempts.append(
            {
                "label": label,
                "error": "missing web tokens",
                "lsd_found": bool(lsd),
                "csrf_found": bool(csrf),
            }
        )
        return {"user": None, "error": "missing web tokens", "attempts": attempts}

    event_request_id = str(uuid.uuid4())
    waterfall_id = str(uuid.uuid4())
    variables = {
        "params": {
            "event_request_id": event_request_id,
            "next_uri": "",
            "search_query": username,
            "waterfall_id": waterfall_id,
        }
    }
    data = {
        "av": "0",
        "__d": "www",
        "__user": "0",
        "__a": "1",
        "__req": "1",
        "dpr": "1",
        "__ccg": "MODERATE",
        "__comet_req": "7",
        "lsd": lsd,
        "jazoest": _jazoest(lsd),
        "__spin_b": "trunk",
        "__crn": "comet.igweb.PolarisCAAIGAccountRecoverySearchRoute",
        "qpl_active_flow_ids": "516759801",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": _RECOVERY_GRAPHQL_FRIENDLY_NAME,
        "server_timestamps": "true",
        "variables": json.dumps(variables, separators=(",", ":")),
        "doc_id": _RECOVERY_GRAPHQL_DOC_ID,
        "fb_api_analytics_tags": json.dumps(["qpl_active_flow_ids=516759801"]),
    }
    headers = _web_headers()
    headers.update(
        {
            "X-ASBD-ID": "359341",
            "X-CSRFToken": csrf,
            "X-FB-Friendly-Name": _RECOVERY_GRAPHQL_FRIENDLY_NAME,
            "X-FB-LSD": lsd,
            "X-IG-Max-Touch-Points": "0",
        }
    )

    try:
        response = session.post(
            "https://www.instagram.com/api/graphql",
            headers=headers,
            data=data,
            timeout=20,
        )
    except requests.RequestException as exc:
        attempts.append({"label": label, "error": f"Network error: {exc}"})
        return {"user": None, "error": f"Network error: {exc}", "attempts": attempts}

    _debug_lookup_response(label, response)
    attempt = {
        "label": label,
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
    }
    attempts.append(attempt)

    if response.status_code == 429:
        attempt["error"] = "rate limit"
        return {"user": None, "error": "rate limit", "attempts": attempts}
    if response.status_code != 200:
        attempt["error"] = f"HTTP {response.status_code}"
        return {"user": None, "error": attempt["error"], "attempts": attempts}

    try:
        payload = response.json()
    except json.JSONDecodeError:
        attempt["error"] = "invalid json"
        return {"user": None, "error": "invalid json", "attempts": attempts}

    if not isinstance(payload, dict):
        attempt["error"] = "unexpected json type"
        return {"user": None, "error": "unexpected json type", "attempts": attempts}

    _debug_lookup_payload(label, payload)
    account_search = (payload.get("data") or {}).get("caa_ar_ig_account_search") or {}
    if not account_search:
        attempt["error"] = "missing caa_ar_ig_account_search"
        attempt["keys"] = sorted(payload.keys())
        return {"user": None, "error": attempt["error"], "attempts": attempts}

    contact_points = account_search.get("contact_points") or []
    profiles = account_search.get("profiles") or []
    attempt["contact_points"] = len(contact_points)
    attempt["profiles"] = len(profiles)
    attempt["eligible_for_ar_code"] = account_search.get("eligible_for_ar_code")
    attempt["search_type"] = account_search.get("search_type")

    normalized_contacts = [
        asdict(_normalize_recovery_contact_point(point, idx))
        for idx, point in enumerate(contact_points, 1)
        if isinstance(point, dict)
    ]
    user = {
        "source": label,
        "search_type": account_search.get("search_type"),
        "eligible_for_ar_code": account_search.get("eligible_for_ar_code"),
        "feta_account_returned": account_search.get("feta_account_returned"),
        "account_type_shown": account_search.get("account_type_shown"),
        "allow_display": account_search.get("allow_display"),
        "cuid": account_search.get("cuid"),
        "cipher": account_search.get("cipher"),
        "contact_points": normalized_contacts,
        "profiles": profiles,
        "obfuscated_email": "",
        "obfuscated_phone": "",
    }
    for contact in normalized_contacts:
        contact_type = contact.get("type", "").upper()
        value = contact.get("contact_point", "")
        if contact_type == "EMAIL" and value and not user["obfuscated_email"]:
            user["obfuscated_email"] = value
        elif (
            contact_type in {"PHONE", "SMS", "WHATSAPP"}
            and value
            and not user["obfuscated_phone"]
        ):
            user["obfuscated_phone"] = value

    if normalized_contacts:
        printer.verbose(
            f"Advanced lookup [{label}] found {len(normalized_contacts)} recovery contact point(s)."
        )
        return {"user": user, "error": None, "attempts": attempts}

    error_content = account_search.get("error_content")
    if error_content:
        attempt["error_content"] = error_content
    return {"user": user, "error": None, "attempts": attempts}


def _debug_lookup_payload(label: str, payload: dict) -> None:
    """Emit useful JSON-level diagnostics for recovery lookup payloads."""
    printer.verbose(
        f"Advanced lookup [{label}] JSON keys: {', '.join(sorted(payload.keys())) or 'none'}"
    )
    for key in (
        "status",
        "message",
        "error_type",
        "error_title",
        "spam",
        "feedback_title",
        "feedback_message",
    ):
        if payload.get(key) not in {None, ""}:
            printer.verbose(f"Advanced lookup [{label}] {key}: {payload.get(key)}")
    printer.debug(
        "Advanced lookup "
        f"[{label}] JSON payload: {json.dumps(payload, ensure_ascii=False)[:1200]}"
    )


def _instagram_advanced_lookup(username: str, session_id: str = "") -> dict:
    """
    Fetch obfuscated recovery contact info from Instagram's lookup endpoint.

    Uses Instagram's mobile lookup endpoint directly so H4X-Tools does not
    depend on an external wrapper package. Multiple payload variants are tried
    because Instagram frequently changes this unauthenticated recovery flow.

    :param username: Instagram username.
    :param session_id: Optional Instagram ``sessionid`` cookie value for diagnostics.
    :return: ``{"user": dict | None, "error": str | None, "attempts": list}``.
    """
    endpoint = "https://i.instagram.com/api/v1/users/lookup/"
    base_headers = {
        "Accept-Language": "en-US",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Host": "i.instagram.com",
        "Connection": "keep-alive",
    }
    header_variants = [
        (
            "modern_mobile",
            base_headers | {"User-Agent": _MOBILE_UA, "X-IG-App-ID": _WEB_IG_APP_ID},
        ),
        (
            "legacy_lookup",
            base_headers
            | {
                "User-Agent": "Instagram 101.0.0.15.120",
                "X-IG-App-ID": "124024574287414",
            },
        ),
    ]
    payload_variants = [
        ("signed_skip_recovery", {"q": username, "skip_recovery": "1"}),
        ("signed_plain_q", {"q": username}),
    ]
    cookie_variants = [("guest", {})]
    if session_id:
        cookie_variants.insert(0, ("session", _session_cookies(session_id)))
    attempts: list[dict] = []

    printer.verbose(
        "Advanced lookup will try recovery endpoint variants: "
        f"headers={', '.join(label for label, _ in header_variants)}; "
        f"cookies={', '.join(label for label, _ in cookie_variants)}; "
        f"payloads={', '.join(label for label, _ in payload_variants)}"
    )
    if session_id:
        printer.verbose(
            "Advanced lookup has a session ID available. It will also try guest/no-cookie "
            "requests because checkpoint_required can be session-specific."
        )

    for header_label, headers in header_variants:
        for cookie_label, cookies in cookie_variants:
            for payload_label, payload in payload_variants:
                label = f"{header_label}/{cookie_label}/{payload_label}"
                data = "signed_body=SIGNATURE." + quote_plus(
                    json.dumps(payload, separators=(",", ":"))
                )
                printer.verbose(
                    f"Advanced lookup [{label}] POST {endpoint} with fields: "
                    + ", ".join(payload.keys())
                )

                try:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        cookies=cookies,
                        data=data,
                        timeout=20,
                    )
                except requests.RequestException as exc:
                    attempts.append({"label": label, "error": f"Network error: {exc}"})
                    printer.warning(f"Advanced lookup [{label}] network error: {exc}")
                    continue

                _debug_lookup_response(label, response)
                attempt = {
                    "label": label,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                }
                attempts.append(attempt)

                json_payload = None
                try:
                    decoded = response.json()
                    if isinstance(decoded, dict):
                        json_payload = decoded
                    else:
                        attempt["error"] = "unexpected json type"
                        printer.verbose(
                            f"Advanced lookup [{label}] unexpected JSON type: "
                            f"{type(decoded).__name__}"
                        )
                except json.JSONDecodeError:
                    if response.status_code not in {400, 401, 403, 404, 429}:
                        attempt["error"] = "invalid json"
                        printer.warning(
                            f"Advanced lookup [{label}] returned non-JSON response. "
                            "Run with --debug to see the body snippet."
                        )

                if json_payload is not None:
                    _debug_lookup_payload(label, json_payload)
                    attempt["keys"] = sorted(json_payload.keys())
                    attempt["message"] = json_payload.get("message")
                    attempt["status"] = json_payload.get("status")
                    attempt["error_type"] = json_payload.get("error_type")
                    attempt["checkpoint_url"] = json_payload.get("checkpoint_url")

                    if json_payload.get("obfuscated_email") or json_payload.get(
                        "obfuscated_phone"
                    ):
                        printer.verbose(
                            f"Advanced lookup [{label}] found obfuscated contact fields."
                        )
                        return {
                            "user": json_payload,
                            "error": None,
                            "attempts": attempts,
                        }

                    message = str(json_payload.get("message", "")).lower()
                    checkpoint_url = str(json_payload.get("checkpoint_url", "")).lower()
                    if message == "no users found":
                        return {
                            "user": json_payload,
                            "error": None,
                            "attempts": attempts,
                        }
                    if message == "checkpoint_required":
                        attempt["error"] = "checkpoint_required"
                        if "unsupported_version" in checkpoint_url:
                            attempt["error"] = (
                                "checkpoint_required: unsupported_version"
                            )
                            printer.verbose(
                                f"Advanced lookup [{label}] hit Instagram unsupported_version checkpoint."
                            )
                        continue

                    printer.verbose(
                        f"Advanced lookup [{label}] returned no obfuscated fields; trying next variant."
                    )

                if response.status_code == 429:
                    attempt["error"] = "rate limit"
                    printer.warning(
                        f"Advanced lookup [{label}] hit HTTP 429 rate limit."
                    )
                    continue
                if response.status_code in {400, 401, 403, 404}:
                    attempt["error"] = (
                        attempt.get("error") or f"HTTP {response.status_code}"
                    )
                    printer.verbose(
                        f"Advanced lookup [{label}] denied/not usable: HTTP {response.status_code}"
                    )
                    continue
                if response.status_code >= 500:
                    attempt["error"] = f"HTTP {response.status_code}"
                    printer.verbose(
                        f"Advanced lookup [{label}] Instagram server error: HTTP {response.status_code}"
                    )
                    continue

    if any(attempt.get("error") == "rate limit" for attempt in attempts):
        return {"user": None, "error": "rate limit", "attempts": attempts}
    if attempts and all(
        str(attempt.get("error", "")).startswith("checkpoint_required")
        for attempt in attempts
    ):
        return {"user": None, "error": "checkpoint_required", "attempts": attempts}
    if any(
        attempt.get("error") == "checkpoint_required: unsupported_version"
        for attempt in attempts
    ):
        return {
            "user": None,
            "error": "unsupported_version checkpoint",
            "attempts": attempts,
        }

    return {"user": None, "error": "lookup failed", "attempts": attempts}


def _fetch_authenticated(
    username: str,
    session_id: str,
    profile: IGProfile,
    comments_limit: int = 20,
) -> None:
    """
    Populate *profile* using Instagram's authenticated private mobile API.

    Fills all basic fields plus business flag, WhatsApp/memorial/new-user
    flags, IGTV count, and public contact details (email / phone).

    :param username:   Instagram username.
    :param session_id: Instagram ``sessionid`` cookie value.
    :param profile:    :class:`IGProfile` to populate in-place.
    :param comments_limit: Maximum comments to fetch per post. Set to 0 to skip comments.
    """
    result = _get_instagram_info(username, session_id)

    if result.get("error"):
        printer.error(f"Instagram authenticated lookup error: {result['error']}")
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

    if profile.user_id:
        printer.info("Fetching recent posts, active stories, highlights, and reels...")
        profile.recent_posts = _fetch_authenticated_posts(
            profile.user_id, session_id, comments_limit=comments_limit
        )
        profile.stories = _fetch_authenticated_stories(profile.user_id, session_id)
        profile.highlights = _fetch_authenticated_highlights(
            profile.user_id, session_id
        )
        profile.reels = _fetch_authenticated_reels(profile.user_id, session_id)


def _format_timestamp(value: int | str) -> str:
    """Render Instagram epoch timestamps when available."""
    if value in {"", None, "N/A"}:
        return ""
    try:
        return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OSError):
        return str(value)


def _shorten(value: str, max_len: int = 120) -> str:
    """Trim long terminal values while keeping enough context for OSINT output."""
    if not value:
        return ""
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def _fetch_advanced_lookup(
    username: str, profile: IGProfile, session_id: str = ""
) -> None:
    """
    Run Instagram's account-recovery lookup to surface obfuscated contact info.

    Tries the web GraphQL recovery endpoint first (more reliable), then falls back
    to mobile API variants if the web path fails or is rate-limited.

    :param username: Instagram username.
    :param profile:  :class:`IGProfile` to populate in-place.
    :param session_id: Optional Instagram ``sessionid`` cookie value.
    """
    printer.info("Running Instagram recovery lookup (obfuscated contact)...")
    all_attempts: list[dict] = []

    result = _instagram_graphql_recovery_lookup(username)
    all_attempts.extend(result.get("attempts", []))

    if result.get("error") not in {"rate limit"}:
        user_data = result.get("user") or {}
        if user_data.get("contact_points"):
            printer.verbose(
                f"Advanced lookup succeeded via web GraphQL with "
                f"{len(user_data.get('contact_points', []))} contact point(s)."
            )
            _process_recovery_lookup_result(profile, user_data, all_attempts)
            return

    printer.info(
        "Web GraphQL recovery unavailable or rate-limited; trying mobile API variants..."
    )
    result = _instagram_advanced_lookup(username, session_id=session_id)
    all_attempts.extend(result.get("attempts", []))

    if all_attempts:
        summary = []
        for attempt in all_attempts:
            label = attempt.get("label", "unknown")
            status = attempt.get("status_code", "network")
            error = attempt.get("error")
            msg = attempt.get("message")
            suffix = f", error={error}" if error else ""
            if msg:
                suffix += f", message={msg}"
            summary.append(f"{label}: {status}{suffix}")
        printer.verbose("Advanced lookup attempts: " + " | ".join(summary))
        printer.debug(
            "Advanced lookup attempts detail: "
            + json.dumps(all_attempts, ensure_ascii=False, default=str)
        )

    if result.get("error") == "rate limit":
        printer.warning(
            "Advanced lookup rate limited. Obfuscated contact info unavailable. "
            "Try again later, use a different network, or run with --debug for details."
        )
        return

    if result.get("error"):
        if result["error"] in {"checkpoint_required", "unsupported_version checkpoint"}:
            printer.warning(
                "Advanced lookup is blocked by Instagram checkpoint_required. "
                "The response points to /web/unsupported_version/, which usually means "
                "Instagram rejected this recovery endpoint/header combination rather than "
                "that the target lacks contact data. The tool tried modern, legacy, "
                "session, and guest variants."
            )
        else:
            printer.warning(
                f"Advanced lookup failed: {result['error']}. "
                "Run with --debug to inspect HTTP status, response snippets, and JSON messages."
            )
        return

    user_data: dict = result.get("user") or {}

    if user_data.get("message") == "No users found":
        printer.warning("Advanced lookup: no users found for this username.")
        return

    _process_recovery_lookup_result(profile, user_data, all_attempts)


def _process_recovery_lookup_result(
    profile: IGProfile, user_data: dict, attempts: list[dict]
) -> None:
    """Extract and populate obfuscated contact fields into the profile."""
    msg = user_data.get("message")
    if msg:
        printer.verbose(f"Advanced lookup message: {msg}")

    obf_email = user_data.get("obfuscated_email", "")
    obf_phone = str(user_data.get("obfuscated_phone", "")).strip()

    if obf_email:
        profile.obfuscated_email = obf_email
        printer.verbose("Advanced lookup populated obfuscated email.")
    if obf_phone and obf_phone not in {"None", "0", ""}:
        profile.obfuscated_phone = obf_phone
        printer.verbose("Advanced lookup populated obfuscated phone.")

    contact_points = user_data.get("contact_points") or []
    if isinstance(contact_points, list):
        for idx, point in enumerate(contact_points, 1):
            if isinstance(point, dict):
                profile.recovery_contact_points.append(
                    _normalize_recovery_contact_point(point, idx)
                )

    if (
        not profile.obfuscated_email
        and not profile.obfuscated_phone
        and not profile.recovery_contact_points
    ):
        keys = ", ".join(sorted(user_data.keys())) or "none"
        printer.warning(
            "Advanced lookup completed but no obfuscated contact fields were present. "
            f"Returned keys: {keys}"
        )
        printer.debug(
            "Advanced lookup final user payload: "
            + json.dumps(user_data, ensure_ascii=False, default=str)[:1500]
        )


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
            profile.recovery_contact_points,
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
        if profile.recovery_contact_points:
            printer.success(
                f"{'Recovery Contacts':<{_KEY_WIDTH}} : {len(profile.recovery_contact_points)}"
            )
            for contact in profile.recovery_contact_points:
                printer.success(
                    f"  {contact.index}. [{contact.type}] {contact.title}: "
                    f"{contact.contact_point}"
                )

    if profile.recent_posts:
        printer.noprefix("")
        printer.section(f"Recent Posts ({len(profile.recent_posts)})")
        for post in profile.recent_posts:
            meta = f"{post.media_type}"
            if post.like_count != "N/A":
                meta += f" | likes: {post.like_count}"
            if post.comment_count != "N/A":
                meta += f" | comments: {post.comment_count}"
            if post.media_items:
                meta += f" | media items: {len(post.media_items)}"
            printer.success(f"Post {post.index} [{meta}]")
            if post.url:
                printer.success(f"  {'URL':<{_KEY_WIDTH - 2}} : {post.url}")
            if posted := _format_timestamp(post.taken_at):
                printer.success(f"  {'Posted At':<{_KEY_WIDTH - 2}} : {posted}")
            if post.caption:
                printer.success(
                    f"  {'Caption':<{_KEY_WIDTH - 2}} : {_shorten(post.caption)}"
                )
            if post.tagged_users:
                printer.success(
                    f"  {'Tagged Users':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"@{u}" for u in post.tagged_users)
                )
            if post.mentions:
                printer.success(
                    f"  {'Mentions':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"@{u}" for u in post.mentions)
                )
            if post.hashtags:
                printer.success(
                    f"  {'Hashtags':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"#{h}" for h in post.hashtags)
                )
            if post.comments:
                printer.success(
                    f"  {'Comments Fetched':<{_KEY_WIDTH - 2}} : {len(post.comments)}"
                )
                for comment in post.comments:
                    when = _format_timestamp(comment.created_at)
                    prefix = f"@{comment.username}" if comment.username else "unknown"
                    if when:
                        prefix += f" [{when}]"
                    likes = (
                        f" | likes: {comment.like_count}"
                        if comment.like_count != "N/A"
                        else ""
                    )
                    printer.success(
                        f"    {comment.index:02d}. {prefix}{likes}: "
                        f"{_shorten(comment.text, 160)}"
                    )
            elif profile.session_used and post.comment_count not in {0, "0", "N/A"}:
                printer.verbose(
                    f"  No comments fetched for post {post.index}; endpoint may be denied."
                )
            printer.noprefix("")
    elif not profile.session_used:
        printer.warning("No recent posts found (account may be private).")

    if profile.stories:
        printer.noprefix("")
        printer.section(f"Active Stories ({len(profile.stories)})")
        for story in profile.stories:
            printer.success(f"Story {story.index} [{story.media_type}]")
            if posted := _format_timestamp(story.taken_at):
                printer.success(f"  {'Posted At':<{_KEY_WIDTH - 2}} : {posted}")
            if story.url:
                printer.success(
                    f"  {'Media URL':<{_KEY_WIDTH - 2}} : {_shorten(story.url, 100)}"
                )
            if story.mentions:
                printer.success(
                    f"  {'Mentions':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"@{u}" for u in story.mentions)
                )
            printer.noprefix("")
    elif profile.session_used:
        printer.info("No active stories found or story access was denied.")

    if profile.highlights:
        printer.noprefix("")
        printer.section(f"Story Highlights ({len(profile.highlights)})")
        for highlight in profile.highlights:
            title = (
                f" - {highlight.highlight_title}" if highlight.highlight_title else ""
            )
            printer.success(
                f"Highlight {highlight.index}{title} [{highlight.media_type}]"
            )
            if posted := _format_timestamp(highlight.taken_at):
                printer.success(f"  {'Posted At':<{_KEY_WIDTH - 2}} : {posted}")
            if highlight.url:
                printer.success(
                    f"  {'Media URL':<{_KEY_WIDTH - 2}} : {_shorten(highlight.url, 100)}"
                )
            if highlight.mentions:
                printer.success(
                    f"  {'Mentions':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"@{u}" for u in highlight.mentions)
                )
            printer.noprefix("")

    if profile.reels:
        printer.noprefix("")
        printer.section(f"Reels ({len(profile.reels)})")
        for reel in profile.reels:
            meta = []
            if reel.play_count != "N/A":
                meta.append(f"plays: {reel.play_count}")
            if reel.like_count != "N/A":
                meta.append(f"likes: {reel.like_count}")
            if reel.comment_count != "N/A":
                meta.append(f"comments: {reel.comment_count}")
            suffix = f" [{', '.join(meta)}]" if meta else ""
            printer.success(f"Reel {reel.index}{suffix}")
            if reel.url:
                printer.success(f"  {'URL':<{_KEY_WIDTH - 2}} : {reel.url}")
            if posted := _format_timestamp(reel.taken_at):
                printer.success(f"  {'Posted At':<{_KEY_WIDTH - 2}} : {posted}")
            if reel.caption:
                printer.success(
                    f"  {'Caption':<{_KEY_WIDTH - 2}} : {_shorten(reel.caption)}"
                )
            if reel.mentions:
                printer.success(
                    f"  {'Mentions':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"@{u}" for u in reel.mentions)
                )
            if reel.hashtags:
                printer.success(
                    f"  {'Hashtags':<{_KEY_WIDTH - 2}} : "
                    + ", ".join(f"#{h}" for h in reel.hashtags)
                )
            printer.noprefix("")

    printer.noprefix("")
    source = (
        "Instagram private API + ensta  (authenticated)"
        if profile.session_used
        else "ensta guest + Instagram recovery lookup"
    )
    printer.info(f"{'Data source':<{_KEY_WIDTH}} : {source}")
    printer.info(f"{'Scraped at':<{_KEY_WIDTH}} : {profile.scraped_at}")


def _ask_session_id() -> str:
    """
    Resolve the Instagram session ID from saved config or user input.

    Saved values live in ``$HOME/.config/h4x-tools/config.json`` by default,
    using the shared H4X-Tools config helper.

    :return: Session ID string, or an empty string for guest mode.
    """
    saved_session = config.get_value(_CONFIG_SECTION, _SESSION_ID_KEY, "")
    if isinstance(saved_session, str) and saved_session.strip():
        printer.info("Saved Instagram session ID found in H4X-Tools config.")
        printer.info("  1 : Use saved session ID")
        printer.info("  2 : Enter a different session ID")
        printer.info("  3 : Delete saved session ID and use guest mode")
        printer.info("  4 : Use guest mode once")
        choice = printer.user_input("Select [1-4] (default = 1) : ").strip()

        match choice:
            case "" | "1":
                return saved_session.strip()
            case "2":
                return _prompt_new_session_id()
            case "3":
                if config.delete_value(_CONFIG_SECTION, _SESSION_ID_KEY):
                    printer.success("Saved Instagram session ID deleted.")
                return ""
            case "4":
                return ""
            case _:
                printer.warning("Invalid choice. Using saved session ID.")
                return saved_session.strip()

    return _prompt_new_session_id()


def _prompt_new_session_id() -> str:
    """
    Prompt for a new Instagram session ID and optionally save it.

    :return: Session ID string, or an empty string for guest mode.
    """
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

    if not session_id:
        return ""

    printer.warning(
        "Session IDs are sensitive cookies. Saving stores it as plaintext in an owner-only config file."
    )
    printer.warning(
        "Do NOT use your primary Instagram session for scanning large/high-volume accounts. Scanning big accounts can generate many requests and may trigger rate limits or account locks. Use a disposable account if possible."
    )
    answer = (
        printer.user_input(
            "Save this session ID to H4X-Tools config for future runs? (y/N) : "
        )
        .strip()
        .lower()
    )
    if answer in {"y", "yes"}:
        if config.set_value(_CONFIG_SECTION, _SESSION_ID_KEY, session_id):
            printer.success(
                f"Session ID saved to {Style.BRIGHT}{config.get_config_file()}{Style.RESET_ALL}"
            )

    return session_id


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
                    if profile.recovery_contact_points:
                        fh.write(
                            f"  Recovery Points : {len(profile.recovery_contact_points)}\n"
                        )
                        for contact in profile.recovery_contact_points:
                            fh.write(
                                f"    {contact.index}. [{contact.type}] {contact.title}: "
                                f"{contact.contact_point}\n"
                            )

                    if profile.recent_posts:
                        fh.write("\nRECENT POSTS\n" + "-" * 40 + "\n")
                        for post in profile.recent_posts:
                            fh.write(
                                f"  [{post.index}] {post.media_type} | {post.url or post.shortcode}\n"
                            )
                            fh.write(
                                f"      Posted   : {_format_timestamp(post.taken_at) or 'N/A'}\n"
                            )
                            fh.write(f"      Likes    : {post.like_count}\n")
                            fh.write(f"      Comments : {post.comment_count}\n")
                            fh.write(
                                f"      Tagged   : {', '.join('@' + u for u in post.tagged_users) or 'N/A'}\n"
                            )
                            fh.write(
                                f"      Mentions : {', '.join('@' + u for u in post.mentions) or 'N/A'}\n"
                            )
                            fh.write(
                                f"      Hashtags : {', '.join('#' + h for h in post.hashtags) or 'N/A'}\n"
                            )
                            if post.caption:
                                fh.write(f"      Caption  : {post.caption}\n")
                            if post.media_items:
                                fh.write("      Media    :\n")
                                for media in post.media_items:
                                    fh.write(
                                        f"        - {media.index}. {media.media_type}: {media.url}\n"
                                    )
                            if post.comments:
                                fh.write(
                                    f"      Fetched Comments ({len(post.comments)}):\n"
                                )
                                for comment in post.comments:
                                    when = (
                                        _format_timestamp(comment.created_at)
                                        or "Unknown"
                                    )
                                    username = (
                                        f"@{comment.username}"
                                        if comment.username
                                        else "unknown"
                                    )
                                    fh.write(
                                        f"        [{comment.index:02d}] [{when}] {username}: {comment.text}\n"
                                    )
                            fh.write("\n")

                    if profile.stories:
                        fh.write("\nACTIVE STORIES\n" + "-" * 40 + "\n")
                        for story in profile.stories:
                            fh.write(
                                f"  [{story.index}] {story.media_type} | {story.url}\n"
                            )
                            fh.write(
                                f"      Posted   : {_format_timestamp(story.taken_at) or 'N/A'}\n"
                            )
                            fh.write(
                                f"      Mentions : {', '.join('@' + u for u in story.mentions) or 'N/A'}\n\n"
                            )

                    if profile.highlights:
                        fh.write("\nSTORY HIGHLIGHTS\n" + "-" * 40 + "\n")
                        for item in profile.highlights:
                            fh.write(
                                f"  [{item.index}] {item.highlight_title or 'Untitled'} | {item.media_type} | {item.url}\n"
                            )
                            fh.write(
                                f"      Posted   : {_format_timestamp(item.taken_at) or 'N/A'}\n"
                            )
                            fh.write(
                                f"      Mentions : {', '.join('@' + u for u in item.mentions) or 'N/A'}\n\n"
                            )

                    if profile.reels:
                        fh.write("\nREELS\n" + "-" * 40 + "\n")
                        for reel in profile.reels:
                            fh.write(f"  [{reel.index}] {reel.url or reel.code}\n")
                            fh.write(
                                f"      Posted   : {_format_timestamp(reel.taken_at) or 'N/A'}\n"
                            )
                            fh.write(f"      Plays    : {reel.play_count}\n")
                            fh.write(f"      Likes    : {reel.like_count}\n")
                            fh.write(f"      Comments : {reel.comment_count}\n")
                            fh.write(
                                f"      Mentions : {', '.join('@' + u for u in reel.mentions) or 'N/A'}\n"
                            )
                            fh.write(
                                f"      Hashtags : {', '.join('#' + h for h in reel.hashtags) or 'N/A'}\n"
                            )
                            if reel.caption:
                                fh.write(f"      Caption  : {reel.caption}\n")
                            if reel.video_url:
                                fh.write(f"      Video URL: {reel.video_url}\n")
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
                        (
                            "recovery_contact_points_count",
                            len(profile.recovery_contact_points),
                        ),
                        ("session_used", profile.session_used),
                        ("scraped_at", profile.scraped_at),
                    ]:
                        writer.writerow([label, val])

                    if profile.recent_posts:
                        writer.writerow([])
                        writer.writerow(
                            [
                                "post_index",
                                "post_id",
                                "post_pk",
                                "shortcode",
                                "post_url",
                                "taken_at",
                                "media_type",
                                "likes",
                                "comments",
                                "media_item_count",
                                "tagged_users",
                                "mentions",
                                "hashtags",
                                "display_url",
                                "video_url",
                                "caption",
                            ]
                        )
                        for post in profile.recent_posts:
                            writer.writerow(
                                [
                                    post.index,
                                    post.id,
                                    post.pk,
                                    post.shortcode,
                                    post.url,
                                    _format_timestamp(post.taken_at),
                                    post.media_type,
                                    post.like_count,
                                    post.comment_count,
                                    len(post.media_items),
                                    ",".join(post.tagged_users),
                                    ",".join(post.mentions),
                                    ",".join(post.hashtags),
                                    post.display_url,
                                    post.video_url,
                                    post.caption,
                                ]
                            )

                    if profile.recovery_contact_points:
                        writer.writerow([])
                        writer.writerow(
                            [
                                "recovery_contact_index",
                                "contact_type",
                                "title",
                                "contact_point",
                            ]
                        )
                        for contact in profile.recovery_contact_points:
                            writer.writerow(
                                [
                                    contact.index,
                                    contact.type,
                                    contact.title,
                                    contact.contact_point,
                                ]
                            )

                        comments = [
                            (post, comment)
                            for post in profile.recent_posts
                            for comment in post.comments
                        ]
                        if comments:
                            writer.writerow([])
                            writer.writerow(
                                [
                                    "post_index",
                                    "post_pk",
                                    "post_shortcode",
                                    "comment_index",
                                    "comment_id",
                                    "comment_pk",
                                    "username",
                                    "user_id",
                                    "full_name",
                                    "created_at",
                                    "likes",
                                    "text",
                                ]
                            )
                            for post, comment in comments:
                                writer.writerow(
                                    [
                                        post.index,
                                        post.pk,
                                        post.shortcode,
                                        comment.index,
                                        comment.id,
                                        comment.pk,
                                        comment.username,
                                        comment.user_id,
                                        comment.full_name,
                                        _format_timestamp(comment.created_at),
                                        comment.like_count,
                                        comment.text,
                                    ]
                                )

                    if profile.stories:
                        writer.writerow([])
                        writer.writerow(
                            [
                                "story_index",
                                "story_id",
                                "story_pk",
                                "code",
                                "taken_at",
                                "media_type",
                                "media_url",
                                "mentions",
                                "accessibility_caption",
                            ]
                        )
                        for story in profile.stories:
                            writer.writerow(
                                [
                                    story.index,
                                    story.id,
                                    story.pk,
                                    story.code,
                                    _format_timestamp(story.taken_at),
                                    story.media_type,
                                    story.url,
                                    ",".join(story.mentions),
                                    story.accessibility_caption,
                                ]
                            )

                    if profile.highlights:
                        writer.writerow([])
                        writer.writerow(
                            [
                                "highlight_index",
                                "highlight_title",
                                "story_id",
                                "story_pk",
                                "code",
                                "taken_at",
                                "media_type",
                                "media_url",
                                "mentions",
                                "accessibility_caption",
                            ]
                        )
                        for item in profile.highlights:
                            writer.writerow(
                                [
                                    item.index,
                                    item.highlight_title,
                                    item.id,
                                    item.pk,
                                    item.code,
                                    _format_timestamp(item.taken_at),
                                    item.media_type,
                                    item.url,
                                    ",".join(item.mentions),
                                    item.accessibility_caption,
                                ]
                            )

                    if profile.reels:
                        writer.writerow([])
                        writer.writerow(
                            [
                                "reel_index",
                                "reel_id",
                                "reel_pk",
                                "code",
                                "url",
                                "taken_at",
                                "plays",
                                "likes",
                                "comments",
                                "mentions",
                                "hashtags",
                                "video_url",
                                "cover_url",
                                "caption",
                            ]
                        )
                        for reel in profile.reels:
                            writer.writerow(
                                [
                                    reel.index,
                                    reel.id,
                                    reel.pk,
                                    reel.code,
                                    reel.url,
                                    _format_timestamp(reel.taken_at),
                                    reel.play_count,
                                    reel.like_count,
                                    reel.comment_count,
                                    ",".join(reel.mentions),
                                    ",".join(reel.hashtags),
                                    reel.video_url,
                                    reel.cover_url,
                                    reel.caption,
                                ]
                            )

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
def scrape(
    target: str,
    session_id: str | None = None,
    fetch_obf: bool | None = None,
    comments_limit: int | None = None,
) -> None:
    """
    Scrapes and aggregates data from an Instagram account.

    Two tracks are supported:

    **Guest track** (no session ID)
      Uses the ``ensta`` Guest API for public profile data and any public recent
      posts exposed by the guest payload. Advanced recovery lookup can optionally
      be run to surface obfuscated e-mail address or phone number tied to the
      account's recovery flow (this lookup is noisy and may alert the target).

    **Authenticated track** (session ID provided)
      Uses Instagram's private mobile API for a richer profile including
      business flags, IGTV count, WhatsApp link status, publicly listed contact
      details, recent posts, post comments, active stories, story highlights,
      and reels. Comments fetching is optional and can increase request volume.

    The session ID is your Instagram ``sessionid`` cookie value.  To find it:
    open Instagram in a browser → DevTools → Application → Cookies →
    copy the value of the ``sessionid`` cookie.

    Results can be exported to ``scraped_data/`` as TXT, CSV, or JSON.

    WARNING: Scanning very large or high-activity Instagram accounts can generate many requests. This can trigger Instagram's rate limits, checkpoint prompts, or lock the account associated with any session ID you provide. Do not use your primary Instagram session for large-scale scans; prefer guest mode, a disposable account session, or reduce the scope of the scrape.

    :param target: The Instagram username to investigate.
    :param session_id: Optional Instagram ``sessionid`` cookie value. When None, the tool will prompt for a session interactively.
    :param fetch_obf: When True, run the advanced recovery lookup for obfuscated contact info. When False, skip it. When None, the tool will prompt interactively.
    :param comments_limit: Maximum comments to fetch per post (0 to skip). When None, the tool will prompt interactively when using an authenticated session.
    """
    target = target.strip().lstrip("@")
    if not target:
        printer.error("Username cannot be empty.")
        return

    printer.noprefix("")
    printer.warning(
        "Caution: Scanning large Instagram accounts can generate many requests and "
        "may cause Instagram to rate-limit, checkpoint, or lock the session/account. "
        "Avoid scanning high-follower/high-post-count accounts with your primary session. "
        "Consider using guest mode, a disposable session, or limiting the scope of the scrape."
    )

    # Resolve the session ID: use the provided value if given, otherwise prompt.
    if session_id is None:
        session_id = _ask_session_id()
    else:
        session_id = str(session_id).strip()
        if session_id:
            printer.info("Using provided session ID for authenticated lookup.")

    # Determine whether to run the advanced (obfuscated) lookup.
    if fetch_obf is None:
        printer.noprefix("")
        printer.section("Data Fetch Options")
        printer.info("Choose which additional data to retrieve for this scrape.")

        answer_obf = (
            printer.user_input(
                "Run advanced recovery lookup for obfuscated contact info? (NOISY — may trigger SMS/alerts) (y/N) : "
            )
            .strip()
            .lower()
        )
        fetch_obf = answer_obf in {"y", "yes"}

    if fetch_obf:
        printer.warning(
            "Advanced recovery lookup is noisy and may trigger account alerts or SMS to the target. "
            "It may also increase the chance of rate-limiting or checkpointing. Proceed only if you accept this risk."
        )
    else:
        printer.verbose("Skipping advanced recovery lookup (obfuscated contact info).")

    # Determine comments fetching behavior. Only relevant for authenticated sessions.
    if comments_limit is None:
        if session_id:
            printer.noprefix("")
            answer_comments = (
                printer.user_input(
                    "Fetch comments for each recent post? (adds extra requests per post and may trigger rate limits) (y/N) : "
                )
                .strip()
                .lower()
            )
            fetch_comments = answer_comments in {"y", "yes"}
            if fetch_comments:
                comment_limit_input = printer.user_input(
                    "Maximum comments to fetch per post [default 20]: "
                ).strip()
                try:
                    comments_limit = (
                        int(comment_limit_input) if comment_limit_input else 20
                    )
                    if comments_limit < 0:
                        comments_limit = 0
                except ValueError:
                    printer.warning(
                        "Invalid number provided; using default of 20 comments per post."
                    )
                    comments_limit = 20

                printer.warning(
                    "Fetching comments increases request volume and may trigger Instagram rate limits or account checkpointing. "
                    "Use conservative limits for large accounts and consider skipping comments entirely if concerned."
                )
            else:
                comments_limit = 0
        else:
            comments_limit = 0
    else:
        # comments_limit was provided by the caller; warn if it's positive.
        try:
            comments_limit = int(comments_limit)
        except (TypeError, ValueError):
            comments_limit = 0
        if comments_limit > 0:
            printer.warning(
                "Fetching comments increases request volume and may trigger Instagram rate limits or account checkpointing. "
                "Use conservative limits for large accounts and consider skipping comments entirely if concerned."
            )

    profile = IGProfile()

    if session_id:
        printer.info(
            f"Authenticated scrape for {Style.BRIGHT}{target}{Style.RESET_ALL}..."
        )
        _fetch_authenticated(target, session_id, profile, comments_limit=comments_limit)
    else:
        printer.info(
            f"Guest scrape for {Style.BRIGHT}{target}{Style.RESET_ALL} "
            "(no session ID — limited data)..."
        )
        _fetch_guest(target, profile)

    # Advanced lookup runs only if requested.
    if fetch_obf:
        _fetch_advanced_lookup(target, profile, session_id=session_id)

    if not profile.username:
        printer.error("No data could be retrieved for this account.")
        return

    _print_profile(profile)

    printer.noprefix("")
    fmt = _ask_export()
    if fmt:
        _export(profile, fmt)
