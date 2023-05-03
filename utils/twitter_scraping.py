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

import snscrape.modules.twitter as snstwitter
from colorama import Fore
import time

""" This module scrapes data from Twitter.
    Options:
    [1] Get information from an account based on the username
    [2] Get the latest tweets based on a specific query (word or sentence)
    [3] Get the latest tweets that were posted from a specific account 
    [4] Get Twitter Trends from user's country
"""


def scraping_options():
    print("\nAvailable Actions: ")
    print("[1] Scraping a specific profile")
    print("[2] Scraping tweets based on text")
    print("[3] Scraping tweets from a specific user")
    print("[4] Get Twitter Trends Of Your Country")
    print("[5] Go Back to Menu")
    option = input("\nEnter your option (1,2,3,4 or 5): \t")

    if option == "1":
        scraping_a_specific_twitter_account()
    elif option == "2":
        scraping_tweets_based_on_query()
    elif option == "3":
        scraping_tweets_from_a_specific_user()
    elif option == "4":
        scraping_twitter_trends()
    elif option == "5":
        pass
    else:
        print(Fore.RED + "Invalid Option! Going back to the main menu")
        print(Fore.CYAN + "\n")
        time.sleep(2)


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
        print(f"[🔹]Account's location: {profile_data.location}")
        print(f"[🔹]Account's profile image URL: {profile_data.profileImageUrl}")
        print(f"[🔹]Account's banner image URL: {profile_data.profileBannerUrl}")
        print(f"[🔹]Account's friends count (accounts they follow): {profile_data.friendsCount}")
        print(Fore.CYAN + "\n")
        time.sleep(2)
    except (AttributeError, ValueError):
        print(Fore.RED + f"We couldn't find {username} on Twitter")
        print(Fore.CYAN + "\n")


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
            if counter == 100:
                break
        if counter == 0:
            print(Fore.RED + f"This list is empty !")
            print(Fore.CYAN + "\n")
        time.sleep(2)
    except (AttributeError, ValueError):
        print(Fore.RED + "Please Enter a Valid Query !")
        print(Fore.CYAN + "\n")


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
        print(Fore.CYAN + "\n")
    if counter == 0:
        print(Fore.RED + f"This list is empty !")
        print(Fore.CYAN + "\n")
    time.sleep(2)


def scraping_twitter_trends():
    all_trends = snstwitter.TwitterTrendsScraper().get_items()
    print(Fore.MAGENTA + "Here are the trends:\n")
    for trend in all_trends:
        print(f"{trend.name} ----> Here is the link: {trend}")
    print(Fore.CYAN + "\n")
    time.sleep(2)


def printing_tweets(tweet, no_of_tweet):
    print(Fore.BLUE + f"Tweet No:{no_of_tweet}")
    print(Fore.MAGENTA + f"[🔹]Posted by: {tweet.user.username}")
    print(f"[🔹]Content: {tweet.content}")
    print(f"[🔹]Posted on: {tweet.date}")
    print(f"[🔹]Tweet URL: {tweet.url}")
    print(f"[🔹]Hashtags: {tweet.hashtags}")
    print(f"[🔹]Total Likes: {tweet.likeCount}")
    print(f"[🔹]Total Replies: {tweet.replyCount}")
    print(f"[🔹]Total Retweets: {tweet.retweetCount}")
    print(f"[🔹]Mentioned Users: ", end=" ")
    try:
        printing_mentioned_users_from_a_tweet(tweet.mentionedUsers)
    except TypeError:
        print("None")
    print(Fore.CYAN + "\n")


def printing_mentioned_users_from_a_tweet(mentioned_users):
    for user in mentioned_users:
        print(user.username + " ", end="")