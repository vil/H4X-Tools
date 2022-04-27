import phonenumbers as p
from phonenumbers import geocoder
from phonenumbers import carrier
from colorama import Fore

class number:
    def __init__(self, no):
        print("\n")
        try:
            ph_no = p .parse(no)
            geo_location = geocoder.description_for_number(ph_no,'en')
            no_carrier = carrier.name_for_number(ph_no,'en')
            print (f"{Fore.GREEN}[*] Country : \t", geo_location)
            print (f"{Fore.GREEN}[*] Sim Provider \t: ", no_carrier)
            return None
        except Exception :
            print(f"{Fore.RED}No data were found for this number!" + Fore.RESET)
            return(f"{Fore.RED}No data were found for this number!" + Fore.RESET)