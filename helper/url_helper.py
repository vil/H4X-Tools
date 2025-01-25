"""
 Copyright (c) 2023-2025. Vili and contributors.

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

import sys
import os
import json
from helper import printer


def read_local_content(path):
    """
    Reads file content from a local file.

    :param path: path to the file
    :return: Content of the file as a string or None if an error occurs.
    """
    try:
        with open(resource_path(path), 'r') as file:
            if path.endswith(".json"):
                content = json.load(file)
            else:
                content = file.read()
        return content
    except Exception as e:
        printer.error(f"An error occurred: {str(e)}")
        return None

# I hate pyinstaller.
def resource_path(relative_path) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
