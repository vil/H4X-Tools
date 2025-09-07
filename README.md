# H4X-Tools

[![GitHub latest commit](https://badgen.net/github/last-commit/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub commits](https://badgen.net/github/commits/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/commit/)
[![GitHub stars](https://badgen.net/github/stars/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/stargazers/)
[![GitHub forks](https://badgen.net/github/forks/vil/H4X-Tools)](https://GitHub.com/vil/H4X-Tools/network/)

Toolkit for scraping, OSINT and more.

Submit feature requests and bugs in the [issues](https://github.com/vil/H4X-Tools/issues) tab.

![](https://github.com/vil/H4X-Tools/blob/master/img/gui-v0.3.2.png)

### Looking for contributors!

If you have any Python knowledge and some time to spend, please be free to contribute by adding your own set of tools
and improvements! Simply fork the repository, code your tool(s)/improvement(s) and open up a pull request!

# Current tools

> [!WARNING]
> Some tools might not work on Windows systems.

| Tool Name           | Description                                                                                                       |
|---------------------|-------------------------------------------------------------------------------------------------------------------|
| Ig Scrape           | Scrapes information from IG accounts                                                                              |
| Web Search          | Searches the internet for the given query.                                                                        |
| Phone Lookup        | Looks up a phone number and returns information about it.                                                         |
| Ip Lookup           | Looks up an IP/domain address and returns information about it.                                                   |
| Port Scanner        | Scans for open ports in a given IP/domain address.                                                                |
| Username Search     | Tries to find a given username from many different websites.                                                      |
| Leak Search			      | Searches if given email/domain has been compromised and leaked.                                                   |
| Email Search        | Efficiently finds registered accounts from a given email. Thanks to [holehe.](https://github.com/megadose/holehe) |
| WhoIs Lookup        | Looks up a domain and returns information about it.                                                               |
| Fake Info Generator | Generates fake information using [Faker](https://pypi.org/project/Faker/).                                        |
| Web Scrape          | Scrapes links from a given url.                                                                                   |
| Wi-Fi Finder        | Scans for nearby Wi-Fi networks.                                                                                  |
| Wi-Fi Vault         | Scans for locally saved Wi-Fi passwords.                                                                          |
| Dir Buster          | Bruteforce directories on a website.                                                                              |
| Local Users			      | Enumerates local user accounts on the current machine.                                                            |
| Help                | Shows the help message.                                                                                           |
| Exit                | Exits the tool.                                                                                                   |

## Setup

> [!IMPORTANT]
> Make sure you have [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) installed on
> your system.
>
> view the [wiki page](https://github.com/vil/H4X-Tools/wiki) for more detailed tutorial.

### Linux

1. Clone the repository: `git clone https://github.com/vil/h4x-tools.git`

2. Change directory into H4X-Tools: `cd h4x-tools`

3. Run the setup script: `sh setup.sh`

### Windows

1. Clone the repository `git clone https://github.com/vil/h4x-tools.git`

2. Change directory into H4X-Tools `cd h4x-tools`

3. Run the setup script `setup.bat`

The setup script will automatically install dependencies and build H4X-Tools as an executable.
You can also run H4X-Tools using Python by doing `python h4xtools.py`.

Dependencies can be installed manually by doing `pip install -r requirements.txt`.

# License

> [This source code is under the GNU General Public License, version 3.](https://www.gnu.org/licenses/gpl-3.0.txt)

-------------------------------------------
THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DON'T USE IT TO DO SOMETHING ILLEGAL!
