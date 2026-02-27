# H4X-Tools

[![GitHub latest commit](https://badgen.net/github/last-commit/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub commits](https://badgen.net/github/commits/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub stars](https://badgen.net/github/stars/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/stargazers/)
[![GitHub forks](https://badgen.net/github/forks/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/network/)

A modular, terminal-based toolkit for OSINT, reconnaissance, and scraping - built in Python, runs on Linux and Windows.

Submit feature requests and bug reports in the [issues](https://github.com/vil/H4X-Tools/issues) tab.

![](https://github.com/vil/H4X-Tools/blob/master/img/gui-v0.3.5.png)

---

## Tools

| # | Tool | Description |
|---|------|-------------|
| 01 | **Ig Scrape** | Two-track Instagram OSINT scraper. **Guest mode** (no login) uses the `ensta` Guest API for public profile data and recent posts. **Authenticated mode** (Instagram `sessionid` cookie) uses [`toutatis`](https://github.com/megadose/toutatis) via Instagram's private mobile API for richer data - business flags, IGTV count, WhatsApp link status, and publicly listed contact details. Both tracks run Toutatis `advanced_lookup` to surface obfuscated email and phone from Instagram's account-recovery flow. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 02 | **Web Reconnaissance** | Multi-mode OSINT search powered by the `ddgs` library. Choose from 7 modes: **General** (free-form), **Person** (12 dorks), **Email** (8 dorks), **Domain** (12 recon dorks), **Username** (12 platform dorks), **Phone Number** (8 dorks), or **Custom Dork** (write your own template). Configurable result count, retry/back-off on rate limits. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 03 | **Phone Lookup** | Validates and analyses a phone number via the `phonenumbers` library (E.164/national/international formats, country, region, carrier, line type, time zones), then runs [`ignorant`](https://github.com/megadose/ignorant) to check social-media platform registrations. |
| 04 | **IP Lookup** | Resolves a hostname or IP address and queries [ipinfo.io](https://ipinfo.io) for geolocation data - city, region, country, coordinates, ISP/organization, postal code, and timezone - with a direct OpenStreetMap link. |
| 05 | **Username Search** | Asynchronously checks a username across hundreds of websites using a bundled site database. All matches (with direct profile URLs) are printed in real time. |
| 06 | **Email Search** | Checks an email address against 100+ websites and services using [`holehe`](https://github.com/megadose/holehe) to identify where the address is registered. |
| 07 | **Leak Search** | Multi-source breach and credential intelligence for an **email address**, **domain**, or **username**. Queries [Hudson Rock Cavalier](https://cavalier.hudsonrock.com) for stealer-log records (date of compromise, stealer family, infected machine details, masked credential samples, corporate/user service counts) and, for email targets, cross-references the [ProxyNova COMB](https://api.proxynova.com/comb) dataset (3.2B+ leaked credential lines) for a total hit count. Configurable inline entry limit; results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 08 | **Port Scanner** | Concurrently scans a user-defined TCP port range (1–N) on any IP or hostname using a 50-thread pool. Open ports are reported in real time. |
| 09 | **WhoIs Lookup** | Performs a WHOIS query on a domain using the `whoisdomain` library and displays registrar, registration/expiry dates, name servers, status, and registrant details. |
| 10 | **Fake Info Generator** | Generates a complete fake identity using [`Faker`](https://pypi.org/project/Faker/) - name, job, company, email, phone, address, credit card, IBAN, and location. |
| 11 | **Web Scrape** | Asynchronously harvests all hyperlinks from a target URL. Optionally crawls every discovered page recursively. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 12 | **Wi-Fi Finder** | Scans for nearby Wi-Fi networks. Uses `netsh` on Windows and `nmcli` on Linux, reporting SSID, signal strength, and security type. The currently connected network is highlighted. |
| 13 | **Wi-Fi Vault** | Dumps saved Wi-Fi passwords stored on the local machine - `netsh` on Windows, `nmcli` on Linux. |
| 14 | **Dir Buster** | Asynchronously bruteforces directory and file paths on a target website using a built-in wordlist, printing every URL that returns HTTP 200. |
| 15 | **Bluetooth Scanner** | Scans for nearby Bluetooth devices via `bluetoothctl` (Linux) and reports device names and MAC addresses. *(Windows support coming soon.)* |
| 16 | **Local Users** | Enumerates all local user accounts on the system. On Linux: username, UID, GID, full name, home directory, shell, and group. On Windows: username, terminal, host, session start time, PID, SID, and domain. |

---

## Setup

> [!IMPORTANT]
> Requires [Python 3.10+](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads).
> See the [wiki](https://github.com/vil/H4X-Tools/wiki) for a step-by-step guide.

### Linux

```sh
git clone https://github.com/vil/h4x-tools.git
cd h4x-tools
sh setup.sh
```

### Windows

```bat
git clone https://github.com/vil/h4x-tools.git
cd h4x-tools
setup.bat
```

The setup scripts install all dependencies and optionally build a standalone executable via PyInstaller. You can also run the toolkit directly with:

```sh
python h4xtools.py
```

Dependencies can be installed manually with:

```sh
pip install -r requirements.txt
```

### Debug mode

Launch with the `--debug` flag to enable verbose output:

```sh
python h4xtools.py --debug
```

---

## Contributing

Contributions are welcome! If you have Python knowledge and want to add a tool or improve an existing one:

1. Fork the repository.
2. Create a branch: `git checkout -b feature/my-tool`
3. Write your code and tests.
4. Open a pull request describing what you added or changed.

Please keep the style consistent with the existing utilities (use `helper/printer.py` for output, `@timer.timer` for the entry point, etc.).

---

## Security notice

Pre-compiled binaries are **not** provided. Downloading pre-built executables from untrusted sources is unsafe - always build from source yourself.

---

## License

> This source code is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt).

**This toolkit is intended for educational and authorised security research purposes only. Do not use it against systems or accounts you do not own or have explicit permission to test.**
