"""
Copyright (c) 2023-2026. Vili and contributors.

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


@timer.timer(require_input=True)
def generate() -> None:
    """
    Generates a fake identity with contact, payment, and location details.

    Thanks to Faker, https://pypi.org/project/Faker/
    """
    fake = Faker()
    printer.info("Generating fake information...")
    time.sleep(1)

    printer.noprefix("")
    printer.section("Identity")
    printer.success(f"Name             : {fake.name()}")
    printer.success(f"Job              : {fake.job()}")
    printer.success(f"Company          : {fake.company()}")

    printer.noprefix("")
    printer.section("Contact")
    printer.success(f"Email            : {fake.email()}")
    printer.success(f"Phone Number     : {fake.phone_number()}")
    printer.success(f"Address          : {fake.address()}")

    printer.noprefix("")
    printer.section("Payment")
    printer.success(f"Card Number      : {fake.credit_card_number()}")
    printer.success(f"Card Type        : {fake.credit_card_provider()}")
    printer.success(f"Expiry Date      : {fake.credit_card_expire()}")
    printer.success(f"Security Code    : {fake.credit_card_security_code()}")
    printer.success(f"IBAN             : {fake.iban()}")
    printer.success(f"BBAN             : {fake.bban()}")

    printer.noprefix("")
    printer.section("Location")
    printer.success(f"Country          : {fake.country()}")
    printer.success(f"City             : {fake.city()}")
