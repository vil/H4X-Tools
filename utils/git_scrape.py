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
import os
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from helper import printer, proxymanager

_SAVE_DIR = Path("scraped_data")

# Upper bounds for GitHub API fetching
_MAX_REPOS_PER_USER: int = 30
_MAX_COMMITS_PER_REPO: int = 500

# ---------------------------------------------------------------------------
# Secret Detection Patterns
# ---------------------------------------------------------------------------

_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Cloud / Infrastructure
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "AWS Secret Access Key",
        re.compile(
            r"(?i)\baws[_\-.]?secret[_\-.]?(?:access[_\-.]?)?key\b.{0,30}[A-Za-z0-9/+=]{40}\b"
        ),
    ),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    (
        "Heroku API Key",
        re.compile(
            r"(?i)heroku.{0,20}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        ),
    ),
    # Source control / CI
    ("GitHub Token (Classic)", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("GitHub OAuth Token", re.compile(r"\bgho_[A-Za-z0-9]{36}\b")),
    ("GitHub Actions Token", re.compile(r"\bghs_[A-Za-z0-9]{36}\b")),
    ("GitHub PAT (Fine-grained)", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b")),
    ("NPM Access Token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    # Messaging
    ("Slack Bot Token", re.compile(r"\bxoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*\b")),
    ("Slack User Token", re.compile(r"\bxoxp-[0-9A-Za-z\-]{30,}\b")),
    (
        "Slack Webhook URL",
        re.compile(
            r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24,}"
        ),
    ),
    ("Telegram Bot Token", re.compile(r"\b[0-9]{8,10}:[A-Za-z0-9_\-]{35}\b")),
    # Payment
    ("Stripe Live Secret Key", re.compile(r"\bsk_live_[0-9a-zA-Z]{24,}\b")),
    ("Stripe Test Secret Key", re.compile(r"\bsk_test_[0-9a-zA-Z]{24,}\b")),
    # Email / Communication
    ("SendGrid API Key", re.compile(r"\bSG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}\b")),
    ("Mailgun API Key", re.compile(r"\bkey-[0-9a-zA-Z]{32}\b")),
    ("Mailchimp API Key", re.compile(r"\b[0-9a-f]{32}-us[0-9]{1,2}\b")),
    # Crypto / Auth
    (
        "Private Key (PEM)",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "JWT Token",
        re.compile(
            r"\beyJ[A-Za-z0-9\-_=]{10,}\.eyJ[A-Za-z0-9\-_=]{10,}\.[A-Za-z0-9\-_.+/=]{10,}"
        ),
    ),
    # Database
    (
        "Database URL",
        re.compile(
            r"(?i)(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|mariadb|redis|amqps?)://[^\s\"'<>]{8,}"
        ),
    ),
    # Generic / catch-all (ordered last to avoid noise masking specific patterns)
    (
        "Generic Password",
        re.compile(r'(?i)(?:password|passwd|pwd)\s*[:=]\s*["\'][^"\']{6,}["\']'),
    ),
    (
        "Generic API Key",
        re.compile(
            r'(?i)(?:api[_\-]?key|apikey)\s*[:=]\s*["\'][A-Za-z0-9\-_.]{16,}["\']'
        ),
    ),
    (
        "Generic Secret",
        re.compile(
            r'(?i)(?:secret[_\-]?key|app[_\-]?secret|client[_\-]?secret|auth[_\-]?secret)\s*[:=]\s*["\'][A-Za-z0-9\-_.]{16,}["\']'
        ),
    ),
    (
        "Generic Token",
        re.compile(
            r'(?i)(?:access[_\-]?token|auth[_\-]?token|bearer[_\-]?token)\s*[:=]\s*["\'][A-Za-z0-9\-_.]{20,}["\']'
        ),
    ),
]

_SENSITIVE_FILE_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".env.staging",
        ".env.development",
        ".env.test",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        ".netrc",
        ".npmrc",
        ".pypirc",
        ".boto",
        "credentials",
        "credentials.json",
        "credentials.yml",
        "credentials.yaml",
        "service-account.json",
        "serviceaccount.json",
        "secrets.json",
        "secrets.yml",
        "secrets.yaml",
        "database.yml",
        "database.json",
        "wp-config.php",
        "local_settings.py",
        ".htpasswd",
        "client_secret.json",
        "google-services.json",
        "GoogleService-Info.plist",
        "keystore.jks",
        "keystore.p12",
        "terraform.tfvars",
    }
)

_SENSITIVE_FILE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pem",
        ".key",
        ".p12",
        ".pfx",
        ".der",
        ".jks",
        ".keystore",
        ".ppk",
    }
)

_SUSPICIOUS_MSG_KEYWORDS: tuple[str, ...] = (
    "password",
    "secret",
    "token",
    "credential",
    "private key",
    "api key",
    "access key",
    "remove key",
    "delete secret",
    "oops",
    "accidentally",
    "forgot to",
    "by mistake",
    "cleanup sensitive",
    "remove sensitive",
    "do not commit",
    "gitignore",
    "env file",
    "sensitive data",
    "confidential",
)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class Commit:
    """A single Git commit record."""

    sha: str = ""
    author_name: str = ""
    author_email: str = ""
    date: str = ""
    message: str = ""


@dataclass
class LeakedSecret:
    """A potential secret or sensitive value detected in git history."""

    commit_sha: str = ""
    file_path: str = ""
    pattern_name: str = ""
    matched_value: str = ""
    date: str = ""
    author: str = ""


@dataclass
class SuspiciousCommit:
    """A commit whose message contains keywords suggesting an accidental leak."""

    sha: str = ""
    author_name: str = ""
    date: str = ""
    message: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class GitHubRepo:
    """Metadata for a GitHub Repository."""

    id: int | str = "N/A"
    name: str = ""
    full_name: str = ""
    owner: str = ""
    private: bool | str = ""
    description: str = "N/A"
    homepage: str = "N/A"
    size: int | str = "N/A"
    stars: int | str = "N/A"
    watchers: int | str = "N/A"
    language: str = "N/A"
    forks: int | str = "N/A"
    open_issues: int | str = "N/A"
    license: str = "N/A"
    topics: list[str] = field(default_factory=list)
    visibility: str = "N/A"
    default_branch: str = "N/A"
    subscribers: int | str = "N/A"
    created_at: str = "N/A"
    updated_at: str = "N/A"
    pushed_at: str = "N/A"


@dataclass
class GitHubProfile:
    """Aggregated data container for a git scrape session."""

    target_type: str = ""
    target_name: str = ""

    # GitHub user profile data (populated for "user" target type only)
    username: str = ""
    id: int | str = "N/A"
    name: str = ""
    bio: str = ""
    company: str = ""
    location: str = ""
    email: str = ""
    hireable: bool | str = ""
    blog: str = ""
    twitter: str = ""
    followers: int | str = "N/A"
    following: int | str = "N/A"
    public_repos: int | str = "N/A"
    public_gists: int | str = "N/A"
    created_at: str = ""
    updated_at: str = ""
    avatar_url: str = ""

    # Analysis results
    leaked_identities: set[str] = field(default_factory=set)
    recent_commits: list[Commit] = field(default_factory=list)
    leaked_secrets: list[LeakedSecret] = field(default_factory=list)
    suspicious_commits: list[SuspiciousCommit] = field(default_factory=list)
    tracked_sensitive_files: list[str] = field(default_factory=list)
    historical_sensitive_files: list[str] = field(default_factory=list)


# TODO: GitLab, Codeberg, etc. support


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------


def _shorten(value: str, max_len: int = 80) -> str:
    """Trim long terminal values."""
    if not value:
        return ""
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def _get_headers(token: str) -> dict[str, str]:
    """
    Construct HTTP headers for GitHub API requests.

    :param token: GitHub Personal Access Token, or empty string for guest mode.
    :return: Dictionary of request headers.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        printer.debug("Using provided GitHub PAT for authentication.")
    else:
        printer.debug("No token provided; executing in guest mode.")
    return headers


def _handle_api_response(response: requests.Response) -> Any | None:
    """
    Validate and parse a GitHub API response.

    :param response: The ``requests.Response`` object.
    :return: Decoded JSON or ``None`` on failure.
    """
    printer.verbose(f"API Request: {response.url} (Status: {response.status_code})")
    if response.status_code == 200:
        return response.json()
    elif response.status_code in {401, 403}:
        printer.warning(
            f"GitHub API Auth/Rate Limit error: {response.json().get('message')}"
        )
    elif response.status_code == 404:
        printer.error("Target not found via GitHub API.")
    else:
        printer.error(f"GitHub API returned status {response.status_code}")
    return None


def _paginate_github(url: str, headers: dict, max_results: int = 1000) -> list:
    """
    Fetch all pages of a GitHub API list endpoint up to ``max_results`` items.

    :param url: Base GitHub API URL. Query params will be appended.
    :param headers: Authorization and Accept headers.
    :param max_results: Hard cap on items returned.
    :return: Aggregated list of JSON objects.
    """
    results: list = []
    page = 1
    joiner = "&" if "?" in url else "?"
    while len(results) < max_results:
        paged_url = f"{url}{joiner}per_page=100&page={page}"
        data = _handle_api_response(
            requests.get(
                paged_url,
                headers=headers,
                proxies=proxymanager.get_requests_proxies(),
                timeout=15,
            )
        )
        if not data or not isinstance(data, list) or not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# Secret Scanning Utilities
# ---------------------------------------------------------------------------


def _is_sensitive_file(path: str) -> bool:
    """Return True if the path matches a known sensitive filename or extension."""
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    return name in _SENSITIVE_FILE_NAMES or ext in _SENSITIVE_FILE_EXTENSIONS


def _scan_text_for_secrets(
    text: str,
    commit_sha: str,
    file_path: str,
    date: str,
    author: str,
) -> list[LeakedSecret]:
    """
    Scan a single line of text against all secret detection patterns.

    The matched value is truncated before storage — enough to verify a finding,
    not enough to reuse the secret directly.

    :return: List of ``LeakedSecret`` objects (may be empty).
    """
    found: list[LeakedSecret] = []
    for pattern_name, pattern in _SECRET_PATTERNS:
        m = pattern.search(text)
        if m:
            raw = m.group(0)
            display_val = (raw[:40] + "...") if len(raw) > 40 else raw
            found.append(
                LeakedSecret(
                    commit_sha=commit_sha,
                    file_path=file_path,
                    pattern_name=pattern_name,
                    matched_value=display_val,
                    date=date,
                    author=author,
                )
            )
    return found


def _flag_suspicious_message(
    sha: str, author_name: str, date: str, msg: str
) -> SuspiciousCommit | None:
    """
    Check a commit message for keywords that may indicate an accidental secret commit.

    :return: A ``SuspiciousCommit`` if keywords were found; otherwise ``None``.
    """
    lower = msg.lower()
    hit_keywords = [kw for kw in _SUSPICIOUS_MSG_KEYWORDS if kw in lower]
    if hit_keywords:
        return SuspiciousCommit(
            sha=sha,
            author_name=author_name,
            date=date,
            message=msg,
            keywords=hit_keywords,
        )
    return None


# ---------------------------------------------------------------------------
# Local Repository Analysis
# ---------------------------------------------------------------------------


def _is_bare_repo(repo_path: str) -> bool:
    """Return True if the git repository at ``repo_path`` is a bare clone."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--is-bare-repository"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() == "true"
    except subprocess.SubprocessError:
        return False


def _check_sensitive_files(repo_path: str) -> tuple[list[str], list[str]]:
    """
    Identify sensitive files tracked or ever-committed in the repository.

    :param repo_path: Path to the git repository.
    :return: Tuple of (currently_tracked, historically_committed_but_removed) lists.
    """
    current: list[str] = []
    historical: list[str] = []

    # Files currently in the index
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        tracked = {f.strip() for f in result.stdout.splitlines() if f.strip()}
        current = sorted(f for f in tracked if _is_sensitive_file(f))
    except subprocess.SubprocessError as e:
        printer.debug(f"ls-files failed: {e}")

    # Files ever added to history (even if since removed or gitignored)
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "--all",
                "--diff-filter=A",
                "--name-only",
                "--pretty=format:",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        current_set = set(current)
        seen: set[str] = set()
        for line in result.stdout.splitlines():
            f = line.strip()
            if not f or f in current_set or f in seen:
                continue
            if _is_sensitive_file(f):
                historical.append(f)
                seen.add(f)
    except subprocess.SubprocessError as e:
        printer.debug(f"Historical sensitive-file scan failed: {e}")

    return current, historical


def _scan_local_diffs(repo_path: str, profile: GitHubProfile) -> None:
    """
    Stream ``git log -p`` across all branches and scan every added line for secrets.
    Suspicious commit messages are also flagged here.

    Uses a sentinel prefix in the ``--pretty`` format to locate commit boundaries
    within the unified diff output without needing one subprocess call per commit.

    :param repo_path: Path to the git repository (bare or working-tree).
    :param profile: Results container; findings are appended in-place.
    """
    printer.info(
        "Scanning commit diffs for potential secrets (this may take a moment)..."
    )
    sep = "GITSCRAPE_COMMIT_BRK"

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "--all",
                "-p",
                "--no-color",
                f"--pretty=tformat:{sep}%H\t%an\t%ae\t%aI\t%s",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired:
        printer.warning(
            "Diff scan timed out after 5 minutes. Partial results may be available."
        )
        return

    if not result.stdout:
        printer.debug("git log -p returned no output.")
        return

    current_sha = ""
    current_author = ""
    current_date = ""
    current_file = ""
    seen_sha: set[str] = set()

    for raw_line in result.stdout.splitlines():
        if raw_line.startswith(sep):
            # New commit boundary — parse metadata
            meta = raw_line[len(sep) :]
            parts = meta.split("\t", 4)
            if len(parts) >= 4:
                current_sha = parts[0]
                an = parts[1]
                ae = parts[2]
                current_date = parts[3]
                msg = parts[4] if len(parts) > 4 else ""
                current_author = f"{an} <{ae}>"

                if current_sha and current_sha not in seen_sha:
                    seen_sha.add(current_sha)
                    flagged = _flag_suspicious_message(
                        current_sha, an, current_date, msg
                    )
                    if flagged:
                        profile.suspicious_commits.append(flagged)
            current_file = ""

        elif raw_line.startswith("+++ b/"):
            # Track which file we're diffing
            current_file = raw_line[6:]

        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            # Added line — scan for secrets
            content = raw_line[1:]
            if not content.strip() or not current_sha:
                continue
            secrets = _scan_text_for_secrets(
                content, current_sha, current_file, current_date, current_author
            )
            profile.leaked_secrets.extend(secrets)

    printer.verbose(
        f"Diff scan complete: {len(profile.leaked_secrets)} potential secret(s), "
        f"{len(profile.suspicious_commits)} suspicious commit message(s)."
    )


def scrape_local_repo(repo_path: str, profile: GitHubProfile) -> None:
    """
    Analyze a local git repository via the git CLI.

    Collects commit authors across all branches, detects sensitive tracked files,
    and runs a full diff scan for secrets.

    :param repo_path: Local filesystem path to the git directory.
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing local/cloned repository at: {repo_path}")
    profile.target_type = "local"
    profile.target_name = os.path.basename(repo_path.rstrip("/\\")) or repo_path

    try:
        if not os.path.isdir(repo_path):
            printer.error(f"Path does not exist: {repo_path}")
            return

        # Collect all commits across all branches
        printer.verbose("Fetching commit history across all branches...")
        result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "--all",
                "--pretty=format:%H\t%an\t%ae\t%aI\t%s",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 4)
            if len(parts) < 4:
                continue
            sha, an, ae, date = parts[0], parts[1], parts[2], parts[3]
            msg = parts[4] if len(parts) > 4 else ""

            profile.leaked_identities.add(f"{an} <{ae}>")
            profile.recent_commits.append(
                Commit(sha=sha, author_name=an, author_email=ae, date=date, message=msg)
            )

        printer.success(
            f"Collected {len(profile.recent_commits)} commit(s) from "
            f"{len(profile.leaked_identities)} unique author(s)."
        )

        # Sensitive file checks (requires a working tree, skip for bare repos)
        if not _is_bare_repo(repo_path):
            current_files, historical_files = _check_sensitive_files(repo_path)
            profile.tracked_sensitive_files.extend(current_files)
            profile.historical_sensitive_files.extend(historical_files)
            if current_files:
                printer.warning(
                    f"Found {len(current_files)} currently-tracked sensitive file(s)!"
                )
            if historical_files:
                printer.warning(
                    f"Found {len(historical_files)} sensitive file(s) in history (since removed)."
                )

        # Full diff scan for secrets and suspicious messages
        _scan_local_diffs(repo_path, profile)

    except subprocess.CalledProcessError as e:
        printer.debug(f"Git execution failed: {e.stderr}")
        printer.error(
            "Failed to execute git commands. Ensure git is installed and this is a valid repo."
        )
    except subprocess.SubprocessError as e:
        printer.error(f"Error reading local repository: {e}")


# ---------------------------------------------------------------------------
# GitHub Scraping
# ---------------------------------------------------------------------------


def _scan_github_gists(gists: list, headers: dict, profile: GitHubProfile) -> None:
    """
    Fetch the content of each gist and scan for potential secrets.

    :param gists: List of gist metadata dicts from the GitHub API.
    :param headers: GitHub API request headers.
    :param profile: Results container; findings appended in-place.
    """
    if not gists:
        return
    printer.verbose(f"Scanning {len(gists)} gist(s) for secrets...")

    for gist in gists:
        gist_id = gist.get("id", "")
        gist_data = _handle_api_response(
            requests.get(
                f"https://api.github.com/gists/{gist_id}",
                headers=headers,
                proxies=proxymanager.get_requests_proxies(),
                timeout=10,
            )
        )
        if not gist_data:
            continue

        owner = gist_data.get("owner", {}).get("login", "")
        updated_at = gist.get("updated_at", "")

        for filename, file_info in gist_data.get("files", {}).items():
            content = file_info.get("content") or ""
            for line in content.splitlines():
                secrets = _scan_text_for_secrets(
                    line,
                    commit_sha=f"gist:{gist_id}",
                    file_path=filename,
                    date=updated_at,
                    author=owner,
                )
                profile.leaked_secrets.extend(secrets)


def scrape_github_user(username: str, token: str, profile: GitHubProfile) -> None:
    """
    Scrape a GitHub user's public profile, repositories, commit history, and gists.

    Fetches up to ``_MAX_REPOS_PER_USER`` repos and ``_MAX_COMMITS_PER_REPO``
    commits per repo. Public gists are also scanned for secrets.

    :param username: Target GitHub account username.
    :param token: GitHub PAT (empty string for guest mode).
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing GitHub account: {username}")
    headers = _get_headers(token)
    profile.target_type = "user"
    profile.target_name = username

    # -- Profile --
    printer.verbose(f"Fetching profile data for: {username}")
    profile_data = _handle_api_response(
        requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers,
            proxies=proxymanager.get_requests_proxies(),
            timeout=10,
        )
    )
    if not profile_data:
        return

    printer.debug(f"Raw profile data: {profile_data}")

    profile.username = profile_data.get("login") or ""
    profile.name = profile_data.get("name") or "N/A"
    profile.id = profile_data.get("id") or "N/A"
    profile.bio = profile_data.get("bio") or "N/A"
    profile.company = profile_data.get("company") or "N/A"
    profile.location = profile_data.get("location") or "N/A"
    profile.email = profile_data.get("email") or "Hidden"
    profile.hireable = profile_data.get("hireable") or "N/A"
    profile.blog = profile_data.get("blog") or "N/A"
    profile.twitter = profile_data.get("twitter_username") or "N/A"
    profile.followers = profile_data.get("followers") or "N/A"
    profile.following = profile_data.get("following") or "N/A"
    profile.public_repos = profile_data.get("public_repos") or "N/A"
    profile.public_gists = profile_data.get("public_gists") or "N/A"
    profile.created_at = profile_data.get("created_at") or "N/A"
    profile.updated_at = profile_data.get("updated_at") or "N/A"
    profile.avatar_url = profile_data.get("avatar_url") or "N/A"

    printer.section("Profile Information")
    printer.success(f"  Username     : {profile.username}")
    printer.success(f"  Name         : {profile.name}")
    printer.success(f"  ID           : {profile.id}")
    printer.success(f"  Bio          : {profile.bio}")
    printer.success(f"  Company      : {profile.company}")
    printer.success(f"  Location     : {profile.location}")
    printer.success(f"  Email        : {profile.email}")
    printer.success(f"  Hireable     : {profile.hireable}")
    printer.success(f"  Blog/Website : {profile.blog}")
    printer.success(f"  Twitter      : {profile.twitter}")
    printer.success(f"  Followers    : {profile.followers}")
    printer.success(f"  Following    : {profile.following}")
    printer.success(f"  Public Repos : {profile.public_repos}")
    printer.success(f"  Public Gists : {profile.public_gists}")
    printer.success(f"  Created At   : {profile.created_at}")
    printer.success(f"  Updated At   : {profile.updated_at}")
    printer.success(f"  Avatar URL   : {profile.avatar_url}")

    # -- Repositories --
    printer.info(f"Fetching up to {_MAX_REPOS_PER_USER} repositories...")
    repos_data = _paginate_github(
        f"https://api.github.com/users/{username}/repos?type=owner&sort=updated",
        headers,
        max_results=_MAX_REPOS_PER_USER,
    )

    if not repos_data:
        printer.warning("No repositories found or unable to fetch.")
    else:
        printer.info(
            f"Scanning {len(repos_data)} repo(s) for leaked identities and secrets..."
        )
        for repo in repos_data:
            repo_name = repo.get("name")
            printer.verbose(f"  Scanning repo: {repo_name}")
            commits_data = _paginate_github(
                f"https://api.github.com/repos/{username}/{repo_name}/commits",
                headers,
                max_results=_MAX_COMMITS_PER_REPO,
            )
            if not commits_data:
                continue

            for commit in commits_data:
                commit_info = commit.get("commit", {})
                author = commit_info.get("author", {})
                email = author.get("email") or ""
                name = author.get("name") or ""
                sha = commit.get("sha") or ""
                date = author.get("date") or ""
                msg = commit_info.get("message", "").split("\n")[0]

                if email and "noreply.github.com" not in email:
                    profile.leaked_identities.add(f"{name} <{email}>")

                profile.recent_commits.append(
                    Commit(
                        sha=sha,
                        author_name=name,
                        author_email=email,
                        date=date,
                        message=msg,
                    )
                )

                flagged = _flag_suspicious_message(sha, name, date, msg)
                if flagged:
                    profile.suspicious_commits.append(flagged)

    # -- Gists --
    printer.info("Fetching public gists...")
    gists_data = _paginate_github(
        f"https://api.github.com/users/{username}/gists",
        headers,
        max_results=100,
    )
    _scan_github_gists(gists_data, headers, profile)


def scrape_github_repo(
    owner: str, repo_name: str, token: str, profile: GitHubProfile
) -> None:
    """
    Scrape metadata and the full paginated commit history of a specific GitHub repository.

    :param owner: Repository owner (user or organization login).
    :param repo_name: Target repository name.
    :param token: GitHub PAT for authentication and rate limits.
    :param profile: Data container to hold findings.
    """
    printer.info(f"Analyzing GitHub repository: {owner}/{repo_name}")
    headers = _get_headers(token)
    profile.target_type = "repository"
    profile.target_name = f"{owner}/{repo_name}"

    # -- Repository metadata --
    repo_data = _handle_api_response(
        requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers=headers,
            proxies=proxymanager.get_requests_proxies(),
            timeout=10,
        )
    )
    if repo_data:
        printer.section("Repository Information")
        printer.success(f"  Full Name      : {repo_data.get('full_name', 'N/A')}")
        printer.success(
            f"  Description    : {_shorten(repo_data.get('description') or 'N/A')}"
        )
        printer.success(f"  Language       : {repo_data.get('language', 'N/A')}")
        printer.success(
            f"  Stars          : {repo_data.get('stargazers_count', 'N/A')}"
        )
        printer.success(f"  Forks          : {repo_data.get('forks_count', 'N/A')}")
        printer.success(
            f"  Open Issues    : {repo_data.get('open_issues_count', 'N/A')}"
        )
        printer.success(f"  Visibility     : {repo_data.get('visibility', 'N/A')}")
        printer.success(f"  Default Branch : {repo_data.get('default_branch', 'N/A')}")
        printer.success(f"  Created At     : {repo_data.get('created_at', 'N/A')}")
        printer.success(f"  Updated At     : {repo_data.get('updated_at', 'N/A')}")
        printer.success(f"  Homepage       : {repo_data.get('homepage') or 'N/A'}")
        topics = repo_data.get("topics") or []
        if topics:
            printer.success(f"  Topics         : {', '.join(topics)}")

    # -- Commit history --
    printer.info(f"Fetching up to {_MAX_COMMITS_PER_REPO} commits...")
    commits_data = _paginate_github(
        f"https://api.github.com/repos/{owner}/{repo_name}/commits",
        headers,
        max_results=_MAX_COMMITS_PER_REPO,
    )
    if not commits_data:
        printer.warning("No commits retrieved.")
        return

    printer.debug(f"Raw commit count: {len(commits_data)}")

    for commit in commits_data:
        commit_info = commit.get("commit", {})
        author = commit_info.get("author", {})
        email = author.get("email") or ""
        name = author.get("name") or ""
        sha = commit.get("sha") or ""
        date = author.get("date") or ""
        msg = commit_info.get("message", "").split("\n")[0]

        if email:
            profile.leaked_identities.add(f"{name} <{email}>")

        profile.recent_commits.append(
            Commit(
                sha=sha, author_name=name, author_email=email, date=date, message=msg
            )
        )

        flagged = _flag_suspicious_message(sha, name, date, msg)
        if flagged:
            profile.suspicious_commits.append(flagged)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


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
    printer.info("  1 : TXT  (human-readable report)")
    printer.info("  2 : CSV  (spreadsheet-friendly)")
    printer.info("  3 : JSON (full structured data)")

    fmt_map = {"1": "txt", "2": "csv", "3": "json", "": "txt"}
    choice = printer.user_input("Choose format (1/2/3) [default: 1] : ").strip()
    return fmt_map.get(choice, "txt")


def _export(profile: GitHubProfile, fmt: str) -> None:
    """Write aggregated scrape results to disk in the chosen format."""
    _SAVE_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]", "_", profile.target_name).strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = _SAVE_DIR / f"git_{safe_name}_{timestamp}"

    leaked_list = sorted(profile.leaked_identities)

    if fmt == "json":
        export_data = asdict(profile)
        # sets are not JSON-serializable; replace with sorted list
        export_data["leaked_identities"] = leaked_list
        out_file = base_path.with_suffix(".json")
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4)
        printer.success(f"Exported JSON to {out_file}")

    elif fmt == "csv":
        out_file = base_path.with_suffix(".csv")
        with out_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Target Type", profile.target_type])
            writer.writerow(["Target Name", profile.target_name])

            if profile.target_type == "user":
                writer.writerow(["Username", profile.username])
                writer.writerow(["Name", profile.name])
                writer.writerow(["ID", profile.id])
                writer.writerow(["Bio", profile.bio])
                writer.writerow(["Company", profile.company])
                writer.writerow(["Location", profile.location])
                writer.writerow(["Email", profile.email])
                writer.writerow(["Hireable", profile.hireable])
                writer.writerow(["Blog", profile.blog])
                writer.writerow(["Twitter", profile.twitter])
                writer.writerow(["Followers", profile.followers])
                writer.writerow(["Following", profile.following])
                writer.writerow(["Public Repos", profile.public_repos])
                writer.writerow(["Public Gists", profile.public_gists])
                writer.writerow(["Created At", profile.created_at])
                writer.writerow(["Updated At", profile.updated_at])
                writer.writerow(["Avatar URL", profile.avatar_url])

            writer.writerow([])
            writer.writerow(["Leaked Identities"])
            for ident in leaked_list:
                writer.writerow([ident])

            writer.writerow([])
            writer.writerow(["Potential Secrets Found"])
            writer.writerow(
                ["SHA", "File", "Pattern", "Value (truncated)", "Date", "Author"]
            )
            for s in profile.leaked_secrets:
                writer.writerow(
                    [
                        s.commit_sha[:7],
                        s.file_path,
                        s.pattern_name,
                        s.matched_value,
                        s.date,
                        s.author,
                    ]
                )

            writer.writerow([])
            writer.writerow(["Suspicious Commit Messages"])
            writer.writerow(["SHA", "Author", "Date", "Message", "Keywords"])
            for sc in profile.suspicious_commits:
                writer.writerow(
                    [
                        sc.sha[:7],
                        sc.author_name,
                        sc.date,
                        sc.message,
                        ", ".join(sc.keywords),
                    ]
                )

            writer.writerow([])
            writer.writerow(["Sensitive Files (Currently Tracked)"])
            for fn in profile.tracked_sensitive_files:
                writer.writerow([fn])

            writer.writerow([])
            writer.writerow(["Sensitive Files (Historical)"])
            for fn in profile.historical_sensitive_files:
                writer.writerow([fn])

            writer.writerow([])
            writer.writerow(["Commits"])
            writer.writerow(["SHA", "Author Name", "Author Email", "Date", "Message"])
            for c in profile.recent_commits:
                writer.writerow(
                    [c.sha, c.author_name, c.author_email, c.date, c.message]
                )

        printer.success(f"Exported CSV to {out_file}")

    else:  # txt
        out_file = base_path.with_suffix(".txt")
        with out_file.open("w", encoding="utf-8") as f:
            f.write("H4X-Tools Git Scrape Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Target Type : {profile.target_type}\n")
            f.write(f"Target Name : {profile.target_name}\n")
            f.write(f"Generated   : {datetime.now().isoformat()}\n\n")

            if profile.target_type == "user":
                f.write("Profile:\n")
                f.write(f"  Username      : {profile.username}\n")
                f.write(f"  Name          : {profile.name}\n")
                f.write(f"  ID            : {profile.id}\n")
                f.write(f"  Bio           : {profile.bio}\n")
                f.write(f"  Company       : {profile.company}\n")
                f.write(f"  Location      : {profile.location}\n")
                f.write(f"  Email         : {profile.email}\n")
                f.write(f"  Hireable      : {profile.hireable}\n")
                f.write(f"  Blog          : {profile.blog}\n")
                f.write(f"  Twitter       : {profile.twitter}\n")
                f.write(f"  Followers     : {profile.followers}\n")
                f.write(f"  Following     : {profile.following}\n")
                f.write(f"  Public Repos  : {profile.public_repos}\n")
                f.write(f"  Public Gists  : {profile.public_gists}\n")
                f.write(f"  Created At    : {profile.created_at}\n")
                f.write(f"  Updated At    : {profile.updated_at}\n")
                f.write(f"  Avatar URL    : {profile.avatar_url}\n\n")

            f.write(f"Leaked Identities ({len(leaked_list)}):\n")
            for ident in leaked_list:
                f.write(f"  {ident}\n")

            f.write(f"\nPotential Secrets ({len(profile.leaked_secrets)}):\n")
            for s in profile.leaked_secrets:
                f.write(
                    f"  [{s.commit_sha[:7]}] {s.file_path or '(unknown)'}"
                    f" | {s.pattern_name} | {s.matched_value}\n"
                )

            f.write(
                f"\nSuspicious Commit Messages ({len(profile.suspicious_commits)}):\n"
            )
            for sc in profile.suspicious_commits:
                f.write(
                    f"  [{sc.sha[:7]}] {sc.date} | {sc.author_name} - {sc.message}\n"
                    f"    Keywords: {', '.join(sc.keywords)}\n"
                )

            if profile.tracked_sensitive_files:
                f.write(
                    f"\nCurrently-tracked Sensitive Files ({len(profile.tracked_sensitive_files)}):\n"
                )
                for fn in profile.tracked_sensitive_files:
                    f.write(f"  [ACTIVE]  {fn}\n")

            if profile.historical_sensitive_files:
                f.write(
                    f"\nHistorically-committed Sensitive Files ({len(profile.historical_sensitive_files)}):\n"
                )
                for fn in profile.historical_sensitive_files:
                    f.write(f"  [REMOVED] {fn}\n")

            f.write(f"\nCommits ({len(profile.recent_commits)}):\n")
            # Cap to 500 lines in the text file for readability
            for c in profile.recent_commits[:500]:
                f.write(
                    f"  [{c.sha[:7]}] {c.date} | {c.author_name} <{c.author_email}> - {c.message}\n"
                )
            if len(profile.recent_commits) > 500:
                f.write(
                    f"  ... ({len(profile.recent_commits) - 500} more commits in full export)\n"
                )

        printer.success(f"Exported TXT to {out_file}")


# ---------------------------------------------------------------------------
# Deep Clone Scan (GitHub repos)
# ---------------------------------------------------------------------------


def _deep_clone_scan(clone_url: str, profile: GitHubProfile) -> None:
    """
    Clone a remote repository into a temporary directory and run a full diff scan.

    :param clone_url: HTTPS or SSH URL to clone from.
    :param profile: Results container; findings are appended in-place.
    """
    printer.info(f"Cloning {clone_url} for deep scan (up to 500 commits)...")
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "500", clone_url, temp_dir],
                capture_output=True,
                check=True,
            )
            _scan_local_diffs(temp_dir, profile)
            current_files, historical_files = _check_sensitive_files(temp_dir)
            profile.tracked_sensitive_files.extend(current_files)
            profile.historical_sensitive_files.extend(historical_files)
        except subprocess.CalledProcessError as e:
            printer.error(
                f"Failed to clone for deep scan. Check the URL and access rights. ({e})"
            )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------


def execute_scrape(target: str | None, repository: str | None, token: str) -> None:
    """
    Determine the type of target and dispatch to the appropriate scraping strategy.

    :param target: GitHub username for profile + multi-repo commit scraping.
    :param repository: GitHub URL, local path, or any other remote git URL.
    :param token: GitHub PAT for API authentication; empty string for guest mode.
    """
    profile = GitHubProfile()

    if repository:
        github_match = re.match(
            r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/\.]+)",
            repository,
        )
        if github_match:
            owner, repo_name = github_match.groups()
            scrape_github_repo(owner, repo_name, token, profile)

            # Offer a deeper local scan by cloning the repo
            printer.noprefix("")
            deep = (
                printer.user_input(
                    "Perform deep secret scan by cloning the repo locally? (y/N) : "
                )
                .strip()
                .lower()
            )
            if deep in {"y", "yes"}:
                _deep_clone_scan(f"https://github.com/{owner}/{repo_name}.git", profile)

        elif os.path.isdir(repository):
            scrape_local_repo(repository, profile)
        else:
            printer.info(
                f"Attempting to clone and analyze remote repository: {repository}"
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    printer.verbose(f"Cloning {repository} into {temp_dir}")
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            "--bare",
                            "--depth",
                            "500",
                            repository,
                            temp_dir,
                        ],
                        capture_output=True,
                        check=True,
                    )
                    scrape_local_repo(temp_dir, profile)
                except subprocess.CalledProcessError:
                    printer.error(
                        "Failed to clone remote repository. Check the URL and access rights."
                    )
                    return

    elif target:
        scrape_github_user(target, token, profile)

    # ---- Summary --------------------------------------------------------
    printer.noprefix("")
    printer.section("Scan Summary")

    if profile.leaked_identities:
        printer.section(f"Leaked Commit Identities ({len(profile.leaked_identities)})")
        for identity in sorted(profile.leaked_identities):
            printer.success(f"  {identity}")
    else:
        printer.warning("No personal identities extracted from commit history.")

    if profile.leaked_secrets:
        printer.section(f"Potential Secrets Found ({len(profile.leaked_secrets)})")
        by_pattern: dict[str, list[LeakedSecret]] = {}
        for s in profile.leaked_secrets:
            by_pattern.setdefault(s.pattern_name, []).append(s)
        for pattern_name, secrets in sorted(by_pattern.items()):
            printer.warning(f"  [{len(secrets):>3}x] {pattern_name}")
            for s in secrets[:3]:
                printer.warning(
                    f"        [{s.commit_sha[:7]}] "
                    f"{s.file_path or '(unknown file)'} | {s.matched_value}"
                )
            if len(secrets) > 3:
                printer.warning(f"        ... and {len(secrets) - 3} more.")
    else:
        printer.success("No potential secrets detected in diff history.")

    if profile.suspicious_commits:
        printer.section(
            f"Suspicious Commit Messages ({len(profile.suspicious_commits)})"
        )
        for sc in profile.suspicious_commits[:10]:
            printer.warning(
                f"  [{sc.sha[:7]}] {sc.date} | {sc.author_name} - {_shorten(sc.message, 60)}"
            )
            printer.warning(f"    Keywords: {', '.join(sc.keywords)}")
        if len(profile.suspicious_commits) > 10:
            printer.warning(f"  ... and {len(profile.suspicious_commits) - 10} more.")
    else:
        printer.success("No suspicious commit messages detected.")

    if profile.tracked_sensitive_files:
        printer.section("Sensitive Files — Currently Tracked!")
        for fn in profile.tracked_sensitive_files:
            printer.error(f"  [ACTIVE]  {fn}")

    if profile.historical_sensitive_files:
        printer.section("Sensitive Files — Previously Committed")
        for fn in profile.historical_sensitive_files:
            printer.warning(f"  [REMOVED] {fn}")

    if profile.recent_commits:
        printer.section(
            f"Recent Commits Sample (top 10 of {len(profile.recent_commits)})"
        )
        for c in profile.recent_commits[:10]:
            printer.success(
                f"  [{c.sha[:7]}] {c.date} | {c.author_name} - {_shorten(c.message)}"
            )

    if profile.target_name:
        printer.noprefix("")
        fmt = _ask_export()
        if fmt:
            _export(profile, fmt)
