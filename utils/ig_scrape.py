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

from colorama import Style
from ensta import Guest
from ensta.lib.Exceptions import APIError, NetworkError, RateLimitedError

from helper import printer, timer

# Pad all profile keys to this width so values line up neatly.
_KEY_WIDTH = 20


@timer.timer(require_input=True)
def scrape(target: str) -> None:
    """
    Scrapes data from an Instagram account.

    :param target: The username of the account to scrape.
    """
    printer.info(f"Scraping profile for {Style.BRIGHT}{target}{Style.RESET_ALL}...")
    try:
        api = Guest()
        data = api.profile(target)
        printer.debug(data)
        print_scraped_data(data.raw)
    except NetworkError as e:
        printer.error(f"Possible network error: {e}")
    except RateLimitedError:
        printer.error("You are being rate limited..!")
    except APIError as e:
        printer.error(f"There is an issue with the API: {e}")
    except AttributeError:
        printer.error(
            "Couldn't get any data. You may need to change IPs or disable your VPN for a while."
        )


def print_scraped_data(data: dict) -> None:
    """
    Prints scraped Instagram profile data in a consistent, aligned format.

    :param data: Raw profile dict from the ensta API.
    """
    readable_data = {
        "Username": data.get("username", "N/A"),
        "User ID": data.get("id", "N/A"),
        "Full Name": data.get("full_name", "N/A"),
        "Biography": data.get("biography", "N/A"),
        "Website": data.get("external_url", "N/A"),
        "Followers": data.get("edge_followed_by", {}).get("count", "N/A"),
        "Following": data.get("edge_follow", {}).get("count", "N/A"),
        "Profile Picture URL": data.get("profile_pic_url_hd", "N/A"),
        "Private": data.get("is_private", "N/A"),
        "Verified": data.get("is_verified", "N/A"),
        "Total Posts": data.get("edge_owner_to_timeline_media", {}).get("count", "N/A"),
    }

    printer.noprefix("")
    printer.section("Instagram Profile")

    for key, value in readable_data.items():
        printer.success(f"{key:<{_KEY_WIDTH}} : {value}")

    # Posts section
    posts = data.get("edge_owner_to_timeline_media", {}).get("edges", [])
    if posts:
        printer.noprefix("")
        printer.section("Recent Posts")

        for idx, post in enumerate(posts, start=1):
            post_node = post.get("node", {})
            shortcode = post_node.get("shortcode", None)
            caption_edges = post_node.get("edge_media_to_caption", {}).get("edges", [])
            caption = (
                caption_edges[0]["node"]["text"] if caption_edges else "No caption"
            )
            post_url = (
                f"https://www.instagram.com/p/{shortcode}/" if shortcode else "No URL"
            )

            printer.success(f"Post {idx}")
            printer.success(f"{'Caption':<{_KEY_WIDTH}} : {caption}")
            printer.success(f"{'URL':<{_KEY_WIDTH}} : {post_url}")
            printer.noprefix("")
    else:
        printer.warning("No posts found or the account is private.")
