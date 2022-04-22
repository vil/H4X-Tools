import requests

def linkedin(name):
    url="http://linkedin.com/in/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Linkedin!")
        print(url + "\n")
    else:
        print("Name not found in Linkedin \n")

def facebook(name):
    url="http://facebook.com/"+name.replace(" ", ".")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Facebook!")
        print(url + "\n")
    else:
        print("Name not found in Facebook \n")

def whitepages(name):
    url="http://whitepages.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Whitepages!")
        print(url + "\n")
    else:
        print("Name not found in Whitepages \n")

def peoplefinders(name):
    url="http://peoplefinders.com/name/"+name.replace(" ", "-")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Peoplefinders!")
        print(url + "\n")
    else:
        print("Name not found in Peoplefinders \n")

def doxbin(name):
    url="http://doxbin.com/upload/"+name.replace(" ", "")
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Name found in Doxbin!")
        print(url + "\n")
    else:
        print("Name not found in Doxbin \n")        