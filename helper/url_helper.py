"""
 Copyright (c) 2023. Vili and contributors.

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

import requests
import random
import json
from helper import printer
from utils import randomuser

BASE_URL = "https://resources.vili.dev/"


def get_file(path):
    """
    Downloads the file from the given url and saves it to the current directory

    :param path: path to the file in BASE_URL (https://resources.vili.dev/)
    """
    try:
        # printer.info(f"Getting file from '{BASE_URL + path}'..!")
        headers = {
            "User-Agent": random.choice(randomuser.users)
        }
        r = requests.get(BASE_URL + path, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        printer.success(f"Successfully downloaded file to '{path}'..!")
    except requests.exceptions.ConnectionError:
        printer.error("Unable to connect to the server..!")


def read_content(path):
    """
    Reads the content of the file from the given url

    :param path: path to the file in BASE_URL (https://resources.vili.dev/)
    """
    try:
        # printer.info(f"Getting file from '{BASE_URL + path}'..!")
        headers = {
            "User-Agent": random.choice(randomuser.users)
        }
        r = requests.get(BASE_URL + path, headers=headers)
        return r.text
    except requests.exceptions.ConnectionError:
        printer.error("Unable to connect to the server..!")


def read_json_content(path):
    """
    Reads the content of a json file from the given url

    :param path: path to the file in BASE_URL (https://resources.vili.dev/)
    """
    try:
        # printer.info(f"Getting file from '{BASE_URL + path}'..!")
        headers = {
            "User-Agent": random.choice(randomuser.users)
        }
        r = requests.get(BASE_URL + path, headers=headers)
        return json.loads(r.text)
    except requests.exceptions.ConnectionError:
        printer.error("Unable to connect to the server..!")
