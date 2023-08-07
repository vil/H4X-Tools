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


def send_request(path):
    """
    Sends a request to the given path and returns the response object.

    :param path: path to the resource in BASE_URL (https://resources.vili.dev/)
    :return: Response object or None if a connection error occurs.
    """
    try:
        headers = {
            "User-Agent": random.choice(randomuser.users)
        }
        response = requests.get(BASE_URL + path, headers=headers)
        return response
    except requests.exceptions.ConnectionError:
        printer.error("Unable to connect to the server..!")
        return None


def get_file(path):
    """
    Downloads the file from the given path and saves it to the current directory.

    :param path: path to the file in BASE_URL (https://resources.vili.dev/)
    """
    response = send_request(path)
    if response is not None:
        try:
            with open(path, 'wb') as f:
                f.write(response.content)
            printer.success(f"Successfully downloaded file to '{path}'..!")
        except OSError:
            printer.error(f"Error while writing to '{path}'")


def read_content(path):
    """
    Reads the content of the file from the given path.

    :param path: path to the file in BASE_URL (https://resources.vili.dev/)
    :return: Content of the file as a string or None if an error occurs.
    """
    response = send_request(path)
    if response is not None:
        return response.text
    return None


def read_json_content(path):
    """
    Reads the content of a JSON file from the given path.

    :param path: path to the JSON file in BASE_URL (https://resources.vili.dev/)
    :return: Content of the JSON file as a dictionary or None if an error occurs.
    """
    response = send_request(path)
    if response is not None:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            printer.error("Error decoding JSON content")
    return None
