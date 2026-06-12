# H4X-Tools

[![GitHub latest commit](https://badgen.net/github/last-commit/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub commits](https://badgen.net/github/commits/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub stars](https://badgen.net/github/stars/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/stargazers/)
[![GitHub forks](https://badgen.net/github/forks/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/network/)

A modular, terminal-based toolkit for OSINT, reconnaissance, and scraping - built in Python, runs on Linux and Windows.

![](https://github.com/vil/vil/blob/master/h4xtools_gui_v26.png?raw=true)

### Sponsors

<table>
  <thead>
    <tr>
      <th>Sponsor</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="500">
        <a href="https://mangoproxy.com/?utm_source=github&utm_medium=partner&utm_campaign=vili">
          <img src="https://raw.githubusercontent.com/vil/vil/refs/heads/master/Banner_MangoProxy.png" alt="MangoProxy" width="500">
        </a>
      </td>
      <td>
        <a href="https://mangoproxy.com/?utm_source=github&utm_medium=partner&utm_campaign=vili"><strong>MangoProxy</strong></a> provides residential, ISP, datacenter, and mobile proxies in 200+ countries. Trusted by businesses worldwide for stable connections, fast response times, and scalable proxy infrastructure. Use promo code <strong>VILI</strong> to get <strong>8% off</strong> Static ISP proxies.
      </td>
    </tr>
    <tr>
      <td width="500">
        <a href="https://www.swiftproxy.net/?ref=H4XTools">
          <img src="https://raw.githubusercontent.com/vil/vil/refs/heads/master/Swiftproxy_banner.png" alt="Swiftproxy" width="500">
        </a>
      </td>
      <td>
        <a href="https://www.swiftproxy.net/?ref=H4XTools"><strong>Swiftproxy</strong></a> provides premium residential proxies with 80M+ IPs across 190+ countries. Supports HTTP, HTTPS, and SOCKS5 with rotating and sticky sessions, non-expiring traffic. Ideal for OSINT, web scraping, automation, data collection, and large-scale online operations. <strong>Free trial</strong> available and <strong>10% off</strong> with code <strong>PROXY90</strong>.
      </td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

## Tools

| # | Tool | Description |
|---|------|-------------|
| 01 | **Ig Scrape** | Two-track Instagram OSINT scraper. **Guest mode** (no login) uses the `ensta` Guest API for public profile data and recent posts. **Authenticated mode** (Instagram `sessionid` cookie) queries Instagram's private mobile API directly for richer data — business flags, IGTV count, WhatsApp link status, public contact details, stories, highlights, and reels. Advanced recovery lookup (obfuscated contact info) and per-post comment fetching are optional to avoid noisy requests. Session IDs can optionally be saved in `$HOME/.config/h4x-tools/config.json`. Use CLI flags `--session-id`, `--skip-obf` (true/false), and `--comments-limit N` for non-interactive runs. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 02 | **Web Reconnaissance** | Multi-mode OSINT search powered by the `ddgs` library. Choose from 7 modes: **General** (free-form), **Person** (12 dorks), **Email** (8 dorks), **Domain** (12 recon dorks), **Username** (12 platform dorks), **Phone Number** (8 dorks), or **Custom Dork** (write your own template). Configurable result count, retry/back-off on rate limits. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 03 | **Phone Lookup** | Validates and analyses a phone number via the `phonenumbers` library (E.164/national/international formats, country, region, carrier, line type, time zones), then runs [`ignorant`](https://github.com/megadose/ignorant) to check social-media platform registrations. |
| 04 | **IP Lookup** | Resolves a hostname or IP address and queries [ipinfo.io](https://ipinfo.io) for geolocation data - city, region, country, coordinates, ISP/organization, postal code, and timezone - with a direct OpenStreetMap link. |
| 05 | **Username Search** | Checks a username across thousands of websites using [`Maigret`](https://github.com/soxoj/maigret)'s maintained site database and detection engines. Configure site count, timeout, parallel connections, retries, and detailed errors before scanning. Results can optionally be exported to `scraped_data/maigret/` as **TXT**, **CSV**, or **JSON**. |
| 06 | **Email Search** | Checks an email address against 100+ websites and services using [`holehe`](https://github.com/megadose/holehe) to identify where the address is registered. |
| 07 | **Leak Search** | Multi-source breach and credential intelligence for an **email address**, **domain**, or **username**. Queries [Hudson Rock Cavalier](https://cavalier.hudsonrock.com) for stealer-log records (date of compromise, stealer family, infected machine details, masked credential samples, corporate/user service counts) and, for email targets, cross-references the [ProxyNova COMB](https://api.proxynova.com/comb) dataset (3.2B+ leaked credential lines) for a total hit count. Configurable inline entry limit; results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
| 08 | **Port Scanner** | Concurrently scans a user-defined TCP port range (1–N) on any IP or hostname using a 50-thread pool. Open ports are reported in real time. |
| 09 | **WhoIs Lookup** | Performs a WHOIS query on a domain using the `whoisdomain` library and displays registrar, registration/expiry dates, name servers, status, and registrant details. |
| 10 | **Fake Info Generator** | Generates a complete fake identity using [`Faker`](https://pypi.org/project/Faker/) - name, job, company, email, phone, address, credit card, IBAN, and location. |
| 11 | **Web Scrape** | Asynchronously harvests all hyperlinks from a target URL, including phone numbers and emails. Optionally crawls every discovered page recursively. Results can be exported to `scraped_data/` as **TXT**, **CSV**, or **JSON**. |
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

### Linux / macOS

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

The setup scripts install all dependencies and create a virtual environment for H4X-Tools. If you prefer to set up a virtual environment manually (recommended), follow these steps.

1. Verify your Python version:

```sh
python --version
# or
python3 --version
```

2. Create a virtual environment in the project directory:

```sh
# Using the standard library venv
# Unix (Linux / macOS)
python3 -m venv .venv

# Windows (PowerShell / cmd)
python -m venv .venv
```

3. Activate the virtual environment:

```sh
# Unix (Linux / macOS)
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat
```

4. Upgrade pip and install dependencies:

```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Run H4X-Tools:

```sh
python h4xtools.py
```

You can also run the toolkit without activating the environment by calling the venv python directly:

```sh
.venv/bin/python h4xtools.py   # Unix
.venv\Scripts\python.exe h4xtools.py   # Windows
```

If you choose not to use a virtual environment, you can install dependencies system-wide with:

```sh
pip install -r requirements.txt
```

### Command-line mode

Run `python h4xtools.py --help` to list all direct-run options. If no tool flag is provided, H4X-Tools opens the interactive menu.

Examples:

```sh
python h4xtools.py --igscrape some_username --verbose
python h4xtools.py --igscrape some_username --comments-limit 5 --skip-obf true --verbose
python h4xtools.py --username some_handle --debug
python h4xtools.py --ip example.com --whois example.com
python h4xtools.py --port-scanner 192.168.1.10 --port-range 1000
```

Tool flags can usually be passed without a value to prompt only for the missing target:

```sh
python h4xtools.py --igscrape --verbose
```

### Debug and verbose mode

Launch with `-v` / `--verbose` for verbose output or `--debug` for debug output:

```sh
python h4xtools.py --verbose
python h4xtools.py --debug
```

---

## Adding a tool

H4X-Tools discovers tools automatically from the `tools/` package. To add one, create a new Python file in `tools/`, subclass `BaseTool`, configure the class metadata, and implement `run()`.

Minimal example:

```py
from helper import printer
from tools.base import BaseTool, ToolArgument


class ExampleTool(BaseTool):
    id = "example"
    name = "Example Tool"
    description = "Prints a provided target."
    order = 99
    aliases = ("--example",)
    arguments = (ToolArgument("target", "TARGET", "Run example for TARGET."),)

    def run(self, target: str | None = None) -> None:
        target = target or printer.user_input("Enter a target : \t")
        printer.info(f"Target: {target}")
```

After saving the file, the tool appears automatically in:

* the interactive menu
* `python h4xtools.py --list-tools`
* `python h4xtools.py --help`
* direct CLI mode via its `aliases`, e.g. `python h4xtools.py --example value`

For larger tools, keep the UI wrapper in `tools/my_tool.py` and place reusable implementation code in `utils/my_tool.py`.

---

## Running with proxies

If you are encountering rate limits or wish to mask your traffic, you can route H4X-Tools through proxies using **ProxyChains**. This tool intercepts the network traffic generated by H4X-Tools and forces it through your specified proxy list.

### 1. Installation

#### Debian / Ubuntu

```sh
sudo apt update
sudo apt install proxychains4 -y
```

#### Arch Linux

```sh
sudo pacman -S proxychains-ng
```

#### Fedora / RHEL

```sh
sudo dnf install proxychains-ng
```

#### Windows

Because ProxyChains relies on UNIX-specific hooks (`LD_PRELOAD`), it does not run natively on standard Windows command lines. You have two primary methods to use it on Windows:

* **Option A: Inside WSL (Recommended)**
If you run H4X-Tools inside the Windows Subsystem for Linux, simply follow the **Ubuntu** installation steps above within your WSL terminal.
* **Option B: Native Windows Port**
You can install a community-maintained Windows port via [Scoop](https://scoop.sh/):
```powershell
scoop install proxychains
```

---

### 2. Configuration

Before running the tool, you need to tell ProxyChains which proxies to use.

1. Open the configuration file in a text editor.
* **Linux / WSL:** `/etc/proxychains4.conf` (Requires `sudo`) or create a local copy at `~/.proxychains/proxychains.conf`.
* **Windows (Scoop):** Located in your scoop application directory (typically `~/scoop/apps/proxychains/current/proxychains.conf`).


2. Scroll to the bottom of the file to the `[ProxyList]` section and add your proxies. For example:

```text
[ProxyList]
# Protocol   Host/IP      Port    Username   Password
# Examples:
socks5       127.0.0.1    9050    # Local Tor service
http         192.168.1.50 8080    # Public or private HTTP proxy
```

> [!TIP]
> You can toggle between `strict_chain` (uses proxies in exact order), `dynamic_chain` (skips dead proxies), or `random_chain` in the configuration file depending on your proxy list reliability.

---

### 3. Usage

Once configured, simply prefix your standard startup command with `proxychains4` (or `proxychains` on Windows):

#### On Linux / WSL:

```sh
proxychains4 python h4xtools.py
```

#### On Windows (via Scoop proxychains port):

```powershell
proxychains python h4xtools.py
```

---

## Contributing

Contributions are welcome! H4X-Tools is designed to be modular, so new tools can be added easily.

### Adding a new tool

1. Fork the repository and create a branch:
   ```sh
   git checkout -b feature/my-tool
   ```
2. Create a new file in `tools/`, for example `tools/my_tool.py`.
3. Subclass `tools.base.BaseTool` and configure the tool metadata:
   * `id` - unique snake_case identifier
   * `name` - display name shown in the menu
   * `description` - help text shown in `--list-tools`
   * `order` - menu position
   * `aliases` - CLI flags, such as `("--my-tool",)`
   * `arguments` - optional `ToolArgument` entries for CLI/input metadata
4. Implement `run()`. Prompt for missing interactive values with `helper/printer.py`.
5. If the tool has larger reusable logic, keep the small UI/metadata wrapper in `tools/my_tool.py` and put the implementation in `utils/my_tool.py`.

H4X-Tools automatically discovers `BaseTool` subclasses from `tools/`, so your tool will appear in the interactive menu, `--help`, `--list-tools`, and direct CLI mode.

### Improving existing tools

* Keep changes focused and avoid unrelated rewrites.
* Preserve existing CLI aliases where possible so users do not lose workflows.
* Use `helper/printer.py` for user-facing output instead of raw `print()` when practical.
* Keep platform-specific behavior clear, especially for Linux/Windows-only functionality.
* Do not hardcode API keys, tokens, credentials, or personal data.

### Before opening a pull request

Run the lightweight checks:

```sh
python -m py_compile h4xtools.py helper/handles.py tools/*.py utils/*.py
python h4xtools.py --help
python h4xtools.py --list-tools --no-internet-check
```

Then open a pull request with:

* a clear summary of what changed
* usage examples or screenshots for user-facing tools
* any new dependencies documented in `requirements.txt`
* notes about platform limitations, network/API usage, rate limits, or required credentials

---

## Security notice

Pre-compiled binaries are **not** provided. Downloading pre-built executables from untrusted sources is unsafe - always build from source yourself.

---

## License

> This source code is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt).

**This toolkit is intended for educational and authorised security research purposes only. Do not use it against systems or accounts you do not own or have explicit permission to test.**
