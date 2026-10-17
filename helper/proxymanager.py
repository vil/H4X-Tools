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

from urllib.parse import urlparse

import requests

from helper import config, printer

_SECTION = "proxies"
_TEST_URL = "https://ipinfo.io"
_REQUEST_TIMEOUT = 10

# In-memory round-robin counter; modded against list length on each call.
_counter: list[int] = [0]

_VALID_SCHEMES = ("http", "https", "socks4", "socks5")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_proxy_list() -> list[str]:
    """Load the saved proxy list from config."""
    raw = config.get_value(_SECTION, "list", default=[])
    if isinstance(raw, list):
        return [str(p) for p in raw if p]
    return []


def _save_proxy_list(proxies: list[str]) -> bool:
    """Persist the proxy list to config."""
    return config.set_value(_SECTION, "list", proxies)


# ---------------------------------------------------------------------------
# Enable / rotation flags
# ---------------------------------------------------------------------------


def is_enabled() -> bool:
    """
    Return whether proxy routing is active.

    :return: ``True`` if proxies are enabled.
    """
    return bool(config.get_value(_SECTION, "enabled", default=False))


def set_enabled(enabled: bool) -> bool:
    """
    Enable or disable proxy routing globally.

    :param enabled: ``True`` to route traffic through proxies.
    :return: ``True`` when the setting was saved successfully.
    """
    return config.set_value(_SECTION, "enabled", enabled)


def is_rotating() -> bool:
    """
    Return whether proxies rotate in round-robin order.

    When rotation is off the first proxy in the list is always used.

    :return: ``True`` if rotation is enabled.
    """
    return bool(config.get_value(_SECTION, "rotate", default=True))


def set_rotating(rotate: bool) -> bool:
    """
    Enable or disable round-robin proxy rotation.

    :param rotate: ``True`` to rotate proxies on each request.
    :return: ``True`` when the setting was saved successfully.
    """
    return config.set_value(_SECTION, "rotate", rotate)


# ---------------------------------------------------------------------------
# Proxy list management
# ---------------------------------------------------------------------------


def list_proxies() -> list[str]:
    """
    Return the saved list of proxy URLs.

    :return: List of proxy URL strings.
    """
    return _load_proxy_list()


def validate_proxy_url(url: str) -> bool:
    """
    Check whether *url* looks like a valid proxy URL.

    Accepted schemes: ``http``, ``https``, ``socks4``, ``socks5``.
    A hostname and explicit port are both required.

    :param url: Proxy URL to validate.
    :return: ``True`` if the URL is well-formed.
    """
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in _VALID_SCHEMES
            and bool(parsed.hostname)
            and parsed.port is not None
        )
    except ValueError:
        return False


def add_proxy(url: str) -> bool:
    """
    Validate and append a proxy URL to the saved list.

    :param url: Proxy URL to add (e.g. ``http://host:3128`` or ``socks5://user:pass@host:1080``).
    :return: ``True`` if the proxy was added successfully.
    """
    url = url.strip()
    if not validate_proxy_url(url):
        printer.error(
            f"Invalid proxy URL: {url!r}  "
            f"Expected: scheme://[user:pass@]host:port  "
            f"(scheme is one of: {', '.join(_VALID_SCHEMES)})"
        )
        return False

    proxies = _load_proxy_list()
    if url in proxies:
        printer.warning("Proxy is already in the list.")
        return False

    proxies.append(url)
    if _save_proxy_list(proxies):
        printer.success(f"Proxy added: {url}")
        return True
    return False


def remove_proxy(index: int) -> bool:
    """
    Remove a proxy by its 0-based position in the list.

    :param index: Zero-based index of the proxy to remove.
    :return: ``True`` if removed successfully.
    """
    proxies = _load_proxy_list()
    if index < 0 or index >= len(proxies):
        printer.error(f"No proxy at index {index}. List has {len(proxies)} entries.")
        return False

    removed = proxies.pop(index)
    if _save_proxy_list(proxies):
        printer.success(f"Proxy removed: {removed}")
        return True
    return False


def clear_proxies() -> bool:
    """
    Remove all saved proxies and reset the rotation counter.

    :return: ``True`` if cleared successfully.
    """
    _counter[0] = 0
    if _save_proxy_list([]):
        printer.success("All proxies cleared.")
        return True
    return False


# ---------------------------------------------------------------------------
# Proxy selection
# ---------------------------------------------------------------------------


def get_proxy() -> str | None:
    """
    Return the next proxy URL to use.

    Applies round-robin rotation when enabled, otherwise always returns the
    first proxy. Returns ``None`` when proxies are disabled or none are
    configured.

    :return: Proxy URL string or ``None``.
    """
    if not is_enabled():
        return None

    proxies = _load_proxy_list()
    if not proxies:
        return None

    if is_rotating():
        index = _counter[0] % len(proxies)
        _counter[0] += 1
    else:
        index = 0

    return proxies[index]


def get_aiohttp_proxy() -> str | None:
    """
    Return the next proxy URL for use with ``aiohttp``.

    aiohttp supports HTTP proxies natively via the ``proxy=`` keyword argument
    on request calls.  SOCKS proxies require the optional ``aiohttp-socks``
    package and are not returned by this helper; use ``get_requests_proxies()``
    with the ``requests`` library for full SOCKS proxy support.

    :return: HTTP(S) proxy URL string, or ``None``.
    """
    proxy = get_proxy()
    if proxy is None:
        return None
    if not proxy.startswith(("http://", "https://")):
        return None
    return proxy


def get_requests_proxies() -> dict[str, str] | None:
    """
    Return a proxies dict ready for use with the ``requests`` library.

    Pass the result directly to the ``proxies`` keyword argument of
    ``requests.get``, ``requests.post``, or a ``requests.Session``.
    Returns ``None`` when proxy use is disabled or no proxies are saved.

    :return: ``{"http": proxy_url, "https": proxy_url}`` or ``None``.
    """
    proxy = get_proxy()
    if proxy is None:
        return None
    return {"http": proxy, "https": proxy}


# ---------------------------------------------------------------------------
# Proxy testing
# ---------------------------------------------------------------------------


def test_proxy(url: str, timeout: int = _REQUEST_TIMEOUT) -> bool:
    """
    Verify that *url* is a reachable, working proxy.

    Sends a request to ``ipinfo.io`` through the proxy and reports the
    apparent exit IP if successful.

    :param url: Proxy URL to test.
    :param timeout: Request timeout in seconds.
    :return: ``True`` if the proxy responded successfully.
    """
    proxies = {"http": url, "https": url}
    try:
        response = requests.get(_TEST_URL, proxies=proxies, timeout=timeout)
        response.raise_for_status()
        ip = response.json().get("ip", "?")
        printer.success(f"OK  {url}  ->  exit IP: {ip}")
        return True
    except requests.exceptions.ProxyError as exc:
        printer.error(f"Proxy error for {url!r}: {exc}")
    except requests.exceptions.Timeout:
        printer.error(f"Timed out after {timeout}s: {url!r}")
    except requests.exceptions.RequestException as exc:
        printer.error(f"Request failed for {url!r}: {exc}")
    return False


def test_all_proxies() -> dict[str, bool]:
    """
    Test every saved proxy and return a pass/fail map.

    :return: Mapping of proxy URL to ``True`` (working) or ``False`` (failed).
    """
    proxies = _load_proxy_list()
    if not proxies:
        printer.warning("No proxies configured.")
        return {}

    results: dict[str, bool] = {}
    for proxy in proxies:
        printer.info(f"Testing {proxy} ...")
        results[proxy] = test_proxy(proxy)

    passed = sum(results.values())
    printer.noprefix("")
    printer.info(f"Results: {passed}/{len(results)} proxies working.")
    return results
