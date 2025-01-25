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

import aiohttp, asyncio
from helper import printer, timer
from colorama import Style


class Spam:
    """
    Spams a given webhook with a given message.

    :param url: The webhook url.
    :param amount: The amount of messages to send.
    :param message: The message to send.
    :param username: The username of the webhook.
    :param throttle_interval: Time interval between sending messages (in seconds).
    """
    @timer.timer
    def __init__(self, url, amount, message, username, throttle_interval=1) -> None:
        self.url = url
        self.amount = amount
        self.message = message
        self.username = username
        self.throttle_interval = throttle_interval

        try:
            printer.info(f"Trying to send {self.amount} messages to {Style.BRIGHT}{self.url}{Style.RESET_ALL}...")
            asyncio.run(self.send_messages())
        except Exception as e:
            printer.error(f"Error: {e}")
        except KeyboardInterrupt:
            printer.error("Cancelled..!")

    async def send_message(self, session, data) -> None:
        async with session.post(self.url, json=data) as response:
            if response.status == 204:
                return True
            else:
                return False

    async def send_messages(self) -> None:
        data = {
            "content": str(self.message),
            "username": str(self.username),
            "avatar_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Elon_Musk_Colorado_2022_%28cropped2%29.jpg/220px-Elon_Musk_Colorado_2022_%28cropped2%29.jpg"
        }

        async with aiohttp.ClientSession() as session:
            success_count = 0
            for _ in range(self.amount):
                result = await self.send_message(session, data)
                if result:
                    success_count += 1
                    printer.success(f"Successfully sent message {success_count} to {Style.BRIGHT}{self.url}{Style.RESET_ALL}..!")
                else:
                    printer.error(f"Failed to send message {success_count + 1} to {Style.BRIGHT}{self.url}{Style.RESET_ALL}..!")

                # Throttle to avoid being rate-limited
                await asyncio.sleep(self.throttle_interval)

            printer.success(f"Successfully sent {success_count} messages to {Style.BRIGHT}{self.url}{Style.RESET_ALL}..!")
            failure_count = self.amount - success_count
            if failure_count > 0:
                printer.error(f"Failed to send {failure_count} messages to {Style.BRIGHT}{self.url}{Style.RESET_ALL}..!")
