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

from helper import config, printer
from tools.base import BaseTool, ToolArgument

_CONFIG_SECTION = "git_scrape"
_TOKEN_KEY = "github_token"


def _prompt_new_token() -> str:
    """
    Prompt for a new GitHub Personal Access Token and optionally save it.

    :return: Token string, or an empty string for guest mode.
    """
    printer.noprefix("")
    printer.info(
        "Provide a GitHub Personal Access Token for higher rate limits and access to private repos."
    )
    printer.info("Generate one at: https://github.com/settings/tokens")
    token = printer.user_input("GitHub Token (leave blank for guest mode) : ").strip()

    if not token:
        return ""

    printer.warning(
        "Tokens are sensitive secrets. Saving stores it as plaintext in an owner-only config file."
    )
    answer = (
        printer.user_input(
            "Save this token to H4X-Tools config for future runs? (y/N) : "
        )
        .strip()
        .lower()
    )
    if answer in {"y", "yes"} and config.set_value(_CONFIG_SECTION, _TOKEN_KEY, token):
        printer.success(
            f"Token saved to {Style.BRIGHT}{config.get_config_file()}{Style.RESET_ALL}"
        )

    return token


def _ask_github_token() -> str:
    """
    Resolve the GitHub Token from saved config or user input.

    Saved values live in ``$HOME/.config/h4x-tools/config.json`` by default,
    using the shared H4X-Tools config helper.

    :return: Token string, or an empty string for guest mode.
    """
    saved_token = config.get_value(_CONFIG_SECTION, _TOKEN_KEY, "")
    if isinstance(saved_token, str) and saved_token.strip():
        printer.info("Saved GitHub Token found in H4X-Tools config.")
        printer.info("  1 : Use saved token")
        printer.info("  2 : Enter a different token")
        printer.info("  3 : Delete saved token and use guest mode")
        printer.info("  4 : Use guest mode once")
        choice = printer.user_input("Select [1-4] (default = 1) : ").strip()

        match choice:
            case "" | "1":
                return saved_token.strip()
            case "2":
                return _prompt_new_token()
            case "3":
                if config.delete_value(_CONFIG_SECTION, _TOKEN_KEY):
                    printer.success("Saved GitHub Token deleted.")
                return ""
            case "4":
                return ""
            case _:
                printer.warning("Invalid choice. Using saved token.")
                return saved_token.strip()

    return _prompt_new_token()


class GitScrape(BaseTool):
    id = "git_scrape"
    name = "Git Scrape"
    order = 17
    aliases = ("--git", "--git-scrape", "--gitscrape")
    description = "Scrapes and analyzes a Git repository (local path, GitHub URL, or any remote URL) or a GitHub account. Detects leaked commit identities, accidental secrets (API keys, tokens, private keys, passwords) in diff history, sensitive tracked files, and suspicious commit messages."
    arguments = (
        ToolArgument(
            "target",
            "USERNAME_OR_PATH_OR_URL",
            "Run Git scrape on a GitHub account / Local repo / Remote repo.",
        ),
    )

    def run(self, target: str | None = None) -> None:
        """
        Execute the Git Scrape tool.

        Resolves user input if parameters are omitted and passes execution
        to the core scrape utility based on the target type.

        :param target: GitHub username, local path, or remote URL to a Git repository.
        """
        from utils import git_scrape

        if not target:
            target = printer.user_input(
                "Enter a GitHub username, local repo path, or repo URL : \t"
            ).strip()

        if not target:
            printer.error("No target provided. Exiting tool.")
            return

        # Dynamically route the single target parameter
        if "/" in target or target.endswith(".git") or target.startswith("http"):
            repo_target = target
            user_target = None
        else:
            repo_target = None
            user_target = target

        token = _ask_github_token()
        git_scrape.execute_scrape(
            target=user_target, repository=repo_target, token=token
        )
