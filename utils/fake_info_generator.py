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

import time
from faker import Faker
from helper import printer, timer


class Generate:
    """
    Generates fake information.

    Thanks to Faker, https://pypi.org/project/Faker/
    """
    @timer.timer
    def __init__(self) -> None:
        fake = Faker()
        printer.info("Generating fake information...")
        time.sleep(1)
        printer.success(f"Fake name : {fake.name()}")
        printer.success(f"Fake address : {fake.address()}")
        printer.success(f"Fake email : {fake.email()}")
        printer.success(f"Fake phone number : {fake.phone_number()}")
        printer.success(f"Fake job : {fake.job()}")
        printer.success(f"Fake company : {fake.company()}")
        printer.success(f"Fake credit card number : {fake.credit_card_number()}")
        printer.success(f"Fake credit card security code : {fake.credit_card_security_code()}")
        printer.success(f"Fake credit card expiration date : {fake.credit_card_expire()}")
        printer.success(f"Fake credit card type : {fake.credit_card_provider()}")
        printer.success(f"Fake IBAN : {fake.iban()}")
        printer.success(f"Fake BIC : {fake.bban()}")
        printer.success(f"Fake country : {fake.country()}")
        printer.success(f"Fake city : {fake.city()}")
