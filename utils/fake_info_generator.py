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

from faker import Faker
import time
from colorama import Fore


class Generate:
    """
    Generates fake information.

    Thanks to Faker, https://pypi.org/project/Faker/
    """
    def __init__(self):
        fake = Faker()
        print(f"{Fore.GREEN}[*] Generating fake information.")
        time.sleep(1)
        print(f"{Fore.GREEN}[*] Fake name : {fake.name()}")
        print(f"{Fore.GREEN}[*] Fake address : {fake.address()}")
        print(f"{Fore.GREEN}[*] Fake email : {fake.email()}")
        print(f"{Fore.GREEN}[*] Fake phone number : {fake.phone_number()}")
        print(f"{Fore.GREEN}[*] Fake job : {fake.job()}")
        print(f"{Fore.GREEN}[*] Fake company : {fake.company()}")
        print(f"{Fore.GREEN}[*] Fake credit card number : {fake.credit_card_number()}")
        print(f"{Fore.GREEN}[*] Fake credit card security code : {fake.credit_card_security_code()}")
        print(f"{Fore.GREEN}[*] Fake credit card expiration date : {fake.credit_card_expire()}")
        print(f"{Fore.GREEN}[*] Fake credit card type : {fake.credit_card_provider()}")
        print(f"{Fore.GREEN}[*] Fake IBAN : {fake.iban()}")
        print(f"{Fore.GREEN}[*] Fake BIC : {fake.bban()}")
        print(f"{Fore.GREEN}[*] Fake country : {fake.country()}")
        print(f"{Fore.GREEN}[*] Fake city : {fake.city()}")
