import requests


def instagram(username):
    url="http://instagram.com/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Instagram")
        print(url + "\n")
    else:
        print("Username not found in Instagram \n")
            

def pinterest(username):
    url="http://pinterest.com/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Pinterest")
        print(url + "\n")
    else:
        print("Username not found in Pinterest \n")

def facebook(username):
    url="http://facebook.com/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Facebook")
        print(url + "\n")
    else:
        print("Username not found in Facebook \n")

def twitter(username):
    url="http://twitter.com/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Twitter")
        print(url + "\n")
    else:    
        print("Username not found in Twitter \n")

def youtube(username):
    url="http://youtube.com/user/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Youtube")
        print(url + "\n")
    else:
        print("Username not found in Youtube \n")

def github(username):
    url="http://github.com/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Github")
        print(url + "\n")
    else:
        print("Username not found in Github \n")

def stackoverflow(username):
    url="http://stackoverflow.com/users/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Stackoverflow")
        print(url + "\n")
    else:
        print("Username not found in Stackoverflow \n")    
        

def linkedin(username):
    url="http://linkedin.com/in/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Linkedin")
        print(url + "\n")
    else:
        print("Username not found in Linkedin \n")

def steam(username):
    url="http://steamcommunity.com/id/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Steam")
        print(url + "\n")
    else:
        print("Username not found in Steam")

def reddit(username):
    url="http://reddit.com/user/"+username
    r = requests.get(url)
    if r.status_code == 200:
        print("[*] Username found in Reddit")
        print(url + "\n")
    else:
        print("Username not found in Reddit \n")                    
        