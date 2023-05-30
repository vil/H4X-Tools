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
import subprocess
from colorama import Fore
import time


class Scan:
    def __init__(self):
        if os.name == "nt":
            print(f"{Fore.GREEN}Windows system detected..!\n")
            time.sleep(1)
            output = subprocess.check_output("netsh wlan show profile", shell=True)
            output = str(output)
            start = output.find("Profile :")
            end = output.find("\\r\\n")
            substring = output[start:end]
            list_of_word = output.split()
            j = 2

            for word in output.split():
                if word == "Profile":
                    next_word = list_of_word[list_of_word.index(word) + j]
                    next_word = next_word.split('\\r\\n')[0]

                    if ':' in next_word:
                        next_word = next_word.split(':')[1]
                        if ' ' in next_word:
                            next_word = next_word.replace(' ', "")
                            print(next_word)
                    wifi = subprocess.check_output('netsh wlan show profile ' + '"' + next_word + '"' + ' key=clear',
                                                   shell=True)
                    print("WiFi Name : ", next_word)
                    wifi = str(wifi)
                    start = wifi.find("Key Content")
                    end = wifi.find("Cost settings")
                    key_content = "Content"
                    substring = wifi[start:end]
                    list_of_words = wifi.split()
                    j = j + 5
                    # print(substring)
                    try:
                        next_word = list_of_words[list_of_words.index(key_content) + 2]
                        i = 2
                        for words in wifi.split():
                            if words == "Content":
                                next_word = list_of_words[list_of_words.index(key_content) + i]
                                next_word = next_word.split('\\r\\n\\r\\nCost')[0]
                                next_word = next_word.replace(' ', "\\ ")
                                i = i + 5
                        print("WiFi Password : ", next_word, "\n")
                    except OSError as e:
                        pass

        else:
            print(f"{Fore.GREEN}Linux system detected..! May ask for sudo.\n")
            time.sleep(1)
            try:
                os.system("sudo grep -r '^psk=' /etc/NetworkManager/system-connections/")
            except OSError as e:
                print(f"{Fore.RED}Error : ", e)
