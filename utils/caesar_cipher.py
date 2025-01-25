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

from colorama import Style
from helper import printer


class CaesarCipher:
    """
    Encrypts or decrypts a text using the Caesar Cipher algorithm.

    :param text: The text to encrypt or decrypt.
    :param shift: The shift to use for the encryption or decryption.
    :param mode: The mode to use for the encryption or decryption.
    """
    def __init__(self, text: str, mode: str) -> None:
        self.text = text
        self.mode = mode

        if self.mode in ("encrypt", "e", "cipher", "c"):
            self.shift = self.get_key()
            printer.info(f"Encrypting the string {Style.BRIGHT}{self.text}{Style.RESET_ALL}...")
            encrypted_text = self.caesar_encrypt(self.text, self.shift)
            printer.success(f"String ciphered in Caesar's code : {Style.BRIGHT}{encrypted_text}{Style.RESET_ALL}")
        elif self.mode in ("decrypt", "d", "decipher"):
            self.shift = self.get_key()
            printer.info(f"Deciphering the string {Style.BRIGHT}{self.text}{Style.RESET_ALL}...")
            decrypted_text = self.caesar_decrypt(self.text, self.shift)
            printer.success(f"{Style.BRIGHT}{self.text}{Style.RESET_ALL} in plain text : {Style.BRIGHT}{decrypted_text}{Style.RESET_ALL}")
        elif self.mode in ("bruteforce", "b"):
            printer.info(f"Bruteforcing the string {Style.BRIGHT}{self.text}{Style.RESET_ALL}...")
            self.brute_force(self.text)
        else:
            printer.error("Invalid mode, please choose either 'encrypt' , 'decrypt' or 'bruteforce'..!")

    @staticmethod
    def get_key() -> int:
        shift = int(printer.inp("Enter a number of shifts (0 to 25) : \t"))
        if shift < 0 or shift > 25:
            printer.error("Invalid shift number, please choose a number between 0 and 25..!")
        return shift

    @staticmethod
    def caesar_encrypt(text, shift) -> str:
        encrypted_text = ""
        for char in text:
            if char.isalpha():
                is_upper = char.isupper()
                char = char.lower()
                encrypted_char = chr(((ord(char) - 97 + shift) % 26) + 97)
                if is_upper:
                    encrypted_char = encrypted_char.upper()
                encrypted_text += encrypted_char
            else:
                encrypted_text += char
        return encrypted_text

    @staticmethod
    def caesar_decrypt(encrypted_text, shift) -> str:
        decrypted_text = ""
        for char in encrypted_text:
            if char.isalpha():
                is_upper = char.isupper()
                char = char.lower()
                decrypted_char = chr(((ord(char) - 97 - shift) % 26) + 97)
                if is_upper:
                    decrypted_char = decrypted_char.upper()
                decrypted_text += decrypted_char
            else:
                decrypted_text += char
        return decrypted_text

    @staticmethod
    def brute_force(encrypted_text) -> None:
        for i in range(26):
            decrypted_text = ""
            for char in encrypted_text:
                if char.isalpha():
                    is_upper = char.isupper()
                    char = char.lower()
                    decrypted_char = chr(((ord(char) - 97 - i) % 26) + 97)
                    if is_upper:
                        decrypted_char = decrypted_char.upper()
                    decrypted_text += decrypted_char
                else:
                    decrypted_text += char
            printer.success(f"{Style.BRIGHT}{decrypted_text}{Style.RESET_ALL} ({i})")
        
        printer.info("Deciphering done, check all the shifts to see which one makes sense.")
