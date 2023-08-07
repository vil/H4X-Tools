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

import time
import random
import requests
from bs4 import BeautifulSoup
from utils.randomuser import users
from helper import printer, timer

headers = {
    "User-Agent": random.choice(users),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://duckduckgo.com/"
}


class Search:
    """
    Searches for a given query on DuckDuckGo.

    :param query: The query to search for.
    """
    @timer.timer
    def __init__(self, query):
        url = f"https://duckduckgo.com/html/?q={query}"

        try:
            response = self.send_request(url)
            if response is not None:
                self.parse_and_print_results(response.text, query)
        except requests.exceptions.RequestException as e:
            printer.error(f"Error : {e}")
        except KeyboardInterrupt:
            printer.error("Cancelled..!")

    @staticmethod
    def send_request(url):
        """
        Send a request to the given URL with appropriate headers.

        :param url: The URL to send the request to.
        :return: The response object if successful, or None.
        """
        try:
            with requests.get(url, headers=headers) as response:
                response.raise_for_status()
                return response
        except requests.exceptions.RequestException:
            return None

    def parse_and_print_results(self, response_text, query):
        """
        Parse the response and print search results.

        :param response_text: The response HTML text.
        :param query: The search query.
        """
        soup = BeautifulSoup(response_text, "html.parser")
        results = soup.find_all("div", {"class": "result__body"})

        if not results:
            printer.error(f"No results found for '{query}'..!")
            return

        printer.info(f"Searching for '{query}' -- With the agent '{headers['User-Agent']}'")
        time.sleep(1)
        for result in results:
            self.print_search_result(result)

    def print_search_result(self, result):
        """
        Prints the result of a search.

        :param result: The result to print.
        """
        title = result.find("a", {"class": "result__a"}).text
        link = result.find("a", {"class": "result__a"})["href"]
        status_code = self.get_status_code(link)
        printer.success(f"'{title}' - {link} - [{status_code}]")

    @staticmethod
    def get_status_code(url):
        """
        Retrieves the status code of a given URL.

        :param url: The URL to check.
        :return: The status code if the request is successful, or None otherwise.
        """
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                return response.status_code
        except requests.exceptions.RequestException:
            return None
