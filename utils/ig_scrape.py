"""
Copyright (c) 2023-2025. Vili and contributors.

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

from helper import printer, timer


@timer.timer(require_input=True)
def scrape(target: str) -> None:
    """
    Scrapes data from an Instagram account.

    :param target: The username of the account to scrape.
    """
    printer.info(
        f"Trying to scrape information about {Style.BRIGHT}{target}{Style.RESET_ALL}..."
    )
    try:
        api = Guest()
        data = api.profile(target)
        # printer.debug(data)
        print_scraped_data(data.raw)
    except Exception as e:
        printer.error(f"Error : {e}")
        return


def print_scraped_data(data) -> None:
    readable_data = {  # Format
        "Username": data.get("username", "N/A"),
        "User ID": data.get("id", "N/A"),
        "Full Name": data.get("full_name", "N/A"),
        "Biography": data.get("biography", "N/A"),
        "Website": data.get("external_url", "N/A"),
        "Followers": data.get("edge_followed_by", {}).get("count", "N/A"),
        "Following": data.get("edge_follow", {}).get("count", "N/A"),
        "Profile Picture URL": data.get("profile_pic_url_hd", "N/A"),
        "Private User?": data.get("is_private", "N/A"),
        "Account Verified?": data.get("is_verified", "N/A"),
        "Total Posts": data.get("edge_owner_to_timeline_media", {}).get("count", "N/A"),
    }

    for key, value in readable_data.items():
        printer.success(f"{key} : {value}")

    # Print posts and links
    posts = data.get("edge_owner_to_timeline_media", {}).get("edges", [])
    if posts:
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

            printer.success(f"Post {idx}: {caption}\nURL: {post_url}\n")
    else:
        printer.warning("No posts found or the account is private.")
