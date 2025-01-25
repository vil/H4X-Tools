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

import base64
from helper import printer
from colorama import Style

class BaseXX:
    """
    Encodes or decodes a text using the Base64/32/16 algorithm.

    :param message: The message to encode or decode.
    :param mode: The mode to use for the encoding or decoding ('encode' or 'decode').
    :param encoding: The encoding to use for the encoding or decoding ('64' or '32' or '16').
    """
    def __init__(self, message, mode, encoding):
        self.message = message
        self.mode = mode
        self.encoding = encoding

        if self.mode in ("encode", "e"):
            printer.info(f"Encoding {Style.BRIGHT}{self.message}{Style.RESET_ALL} into Base{self.encoding}...")
            self.encode()
        elif self.mode in ("decode", "d"):
            printer.info(f"Decoding {Style.BRIGHT}{self.message}{Style.RESET_ALL} from Base{self.encoding}...")
            self.decode()
        else:
            printer.error(f"Invalid mode, please choose either ENCODE or DECODE..!")

    def encode(self):
        try:
            if self.encoding in ("64", "32", "16"):
                encoding_method = getattr(base64, f'b{self.encoding}encode')
                self.encoded_message = encoding_method(self.message.encode("ascii")).decode("ascii")
                printer.success(f"Encoded with Base{self.encoding} : {Style.BRIGHT}{self.encoded_message}{Style.RESET_ALL}")
            else:
                printer.error("Invalid encoding, please choose either : 64, 32, or 16..!")
        except UnicodeEncodeError:
            printer.error("Invalid character, please only use ASCII characters.")

    def decode(self):
        try:
            if self.encoding in ("64", "32", "16"):
                decoding_method = getattr(base64, f'b{self.encoding}decode')
                self.decoded_message = decoding_method(self.message.encode("ascii")).decode("ascii")
                printer.success(f"Decoded from Base{self.encoding} : {Style.BRIGHT}{self.decoded_message}{Style.RESET_ALL}")
            else:
                printer.error("Invalid encoding, please choose either : 64, 32, or 16..!")
        except Exception:
            printer.error("Error while decoding, please make sure the message is encoded in Base64.")

