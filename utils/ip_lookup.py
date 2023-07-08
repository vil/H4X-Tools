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

import json
import time
from urllib.request import urlopen
from helper import printer


class Lookup:
    """
    Gets information about a given ip address using ip-api.com.

    :param ip: The ip address to search for.
    """
    def __init__(self, ip):
        try:
            url = "http://ip-api.com/json/" + ip
            values = json.load(urlopen(url))

            printer.info(f"Trying to find information for '{ip}'")
            time.sleep(1)
            printer.success(f"Ip Address - ", values['query'])
            printer.success(f"Country - ", values['country'])
            printer.success(f"City - ", values['city'])
            printer.success(f"ISP - ", values['isp'])
            printer.success(f"Region - ", values['regionName'])
            printer.success(f"Timezone - ", values['timezone'])
            printer.success(f"Zip - ", values['zip'])
            printer.success(f"Lat - ", values['lat'])
            printer.success(f"Lon - ", values['lon'])
            printer.success(f"AS - ", values['as'])
            printer.success(f"Maps URL - ", f"https://www.google.com/maps/search/{values['lat']},{values['lon']}")

        except Exception as e:
            printer.error(f"Error : ", e)
            pass
