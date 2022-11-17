import snscrape.modules.twitter as snstwitter
from colorama import Fore
import time

""" This module scrapes data from Twitter.
    Options:
    [1] Get information from an account based on the username
    [2] Get the latest tweets based on a specific query (word or sentence)
    [3] Get the latest tweets that were posted from a specific account 
"""


def scraping_options():
    print("\nAvailable Actions: ")
    print("[1] Scraping a specific profile")
    print("[2] Scraping tweets based on text")
    print("[3] Scraping tweets from a specific user")
    print("[4] Go Back to Menu ")
    option = input("\nEnter your option (1,2,3 or 4): \t")

    if option == "1":
        scraping_a_specific_twitter_account()
    elif option == "2":
        scraping_tweets_based_on_query()
    elif option == "3":
        scraping_tweets_from_a_specific_user()
    elif option == "4":
        pass
    else:
        print(Fore.RED + "Invalid Option! Going back to the main menu")
        time.sleep(1)


def scraping_a_specific_twitter_account():
    username = input("Enter the username: ")
    try:
        profile_scraping = snstwitter.TwitterUserScraper(username=username)
        profile_data = profile_scraping._get_entity()
        print(Fore.MAGENTA + f"\n------>Scraping data from the account {profile_data.username}<------")
        print(f"[🔹]Profile Description: {profile_data.rawDescription}")
        print(f"[🔹]Profile Is Verified: {profile_data.verified}")
        print(f"[🔹]Total Followers: {profile_data.followersCount}")
        print(f"[🔹]Account Was Created on: {profile_data.created}")
        time.sleep(2)
    except (AttributeError, ValueError):
        print(Fore.RED + f"We couldn't find {username} on Twitter")


def scraping_tweets_based_on_query():
    text = input("Enter a query: ")
    print(f"\n------>100 most recent tweets that contain the query {text}<------")
    print("\n")
    counter = 0
    try:
        tweets_based_on_text = snstwitter.TwitterSearchScraper(text).get_items()
        for tweet in tweets_based_on_text:
            counter += 1
            printing_tweets(tweet, counter)
            counter += 1
            printing_tweets(tweet, counter)
            if counter == 100:
                break
        if counter == 0:
            print(Fore.RED + f"This list is empty !")
        time.sleep(1)
    except (AttributeError, ValueError):
        print(Fore.RED + "Please Enter a Valid Query !")


def scraping_tweets_from_a_specific_user():
    username = input("Enter the username: ")
    if username == "":
        print(Fore.RED + "This is not a valid name !")
        return
    print(f"\n------>100 most recent tweets from {username}<------")
    counter = 0
    try:
        tweets_from_user = snstwitter.TwitterSearchScraper(f"from:{username}").get_items()
        for tweet in tweets_from_user:
            counter += 1
            printing_tweets(tweet, counter)
            if counter == 100:
                break
    except (AttributeError, ValueError):
        print(Fore.RED + f"We couldn't find {username} on Twitter")
    if counter == 0:
        print(Fore.RED + f"This list is empty !")
    time.sleep(1)


def printing_tweets(tweet, no_of_tweet):
    print(Fore.BLUE + f"Tweet No:{no_of_tweet}")
    print(Fore.MAGENTA + f"[🔹]Posted by: {tweet.user.username}")
    print(f"[🔹]Content: {tweet.content}")
    print(f"[🔹]Posted on: {tweet.date}")
    print(f"[🔹]Tweet URL: {tweet.url}")
    print("\n")
