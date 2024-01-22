"""
 Copyright (c) 2024. Vili and contributors.

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

import base64
from helper import printer


class BaseXX:
    """
    Encodes or decodes a text using the Base64/32/16 algorithm.

    :param message: The message to encode or decode.
    :param mode: The mode to use for the encoding or decoding ('encrypt' or 'decrypt').
    :param encoding: The encoding to use for the encoding or decoding ('base64' or 'base32' or 'base16').
    """
    def __init__(self, message, mode, encoding):
        self.message = message
        self.mode = mode
        self.encoding = encoding

        if self.mode in ("encode", "e"):
            printer.info(f"Encoding '{self.message}' into Base{encoding}...")
            self.encode()
        elif self.mode in ("decode", "d"):
            printer.info(f"Decoding '{self.message}' from Base{encoding}...")
            self.decode()
        else:
            printer.error("Invalid mode, please choose either 'encode' or 'decrypt'..!")

    def encode(self):
        try:
            if self.encoding == "64":
                self.encoded_message = base64.b64encode(self.message.encode("ascii")).decode("ascii")
            elif self.encoding == "32":
                self.encoded_message = base64.b32encode(self.message.encode("ascii")).decode("ascii")
            elif self.encoding == "16":
                self.encoded_message = base64.b16encode(self.message.encode("ascii")).decode("ascii")
            else:
                printer.error("Invalid encoding, please choose either '64' or '32' or '16'..!")
            printer.success(f"'{self.message}' in Base{self.encoding} : {self.encoded_message}")
        except UnicodeEncodeError:
            printer.error("Invalid character, please only use ASCII characters.")

    def decode(self):
        try:
            if self.encoding == "64":
                self.decoded_message = base64.b64decode(self.message.encode("ascii")).decode("ascii")
            elif self.encoding == "32":
                self.decoded_message = base64.b32decode(self.message.encode("ascii")).decode("ascii")
            elif self.encoding == "16":
                self.decoded_message = base64.b16decode(self.message.encode("ascii")).decode("ascii")
            printer.success(f"'{self.message}' in plain text : {self.decoded_message}")
        except Exception:
            printer.error("Error while decoding, please make sure the message is encoded in Base64.")
