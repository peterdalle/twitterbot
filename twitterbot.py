#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twython import Twython, TwythonError
import feedparser
import csv
import datetime
import os
import re
import sys
import time
from datetime import date

class Settings:
	"""
	Twitter bot application settings.
	
	Enter the RSS feed you want to tweet, or keywords you want to retweet.
	"""
	FeedUrl = "http://example.net/feed/"               # RSS feed to read and post tweets from.
	PostedUrlsOutputFile = "posted-urls.log"           # Log file to save all tweeted RSS links (one URL per line).
	PostedRetweetsOutputFile = "posted-retweets.log"   # Log file to save all retweeted tweets (one tweetid per line).
	RetweetIncludeWords = ["#hashtag"]                 # Include tweets with these words when retweeting.
	RetweetExcludeWords = []                           # Do not include tweets with these words when retweeting.

class TwitterAuth:
	"""
	Twitter authentication settings.

	Create a Twitter app at https://apps.twitter.com/ and generate key, secret etc. and insert them here.
	"""
	ConsumerKey = "XXX"
	ConsumerSecret = "XXX"
	AccessToken = "XXX"
	AccessTokenSecret = "XXX"

def compose_message(rss_item):
	"""Compose a tweet from title, link, and description, and then return the final tweet message."""
	title, link, description = rss_item["title"], rss_item["link"], rss_item["description"]
	message = shorten_text(title, maxlength=250) + " " + link
	return message

def shorten_text(text, maxlength):
	"""Truncate text and append three dots (...) at the end if length exceeds maxlength chars."""
	return (text[:maxlength] + '...') if len(text) > maxlength else text

def post_tweet(message):
	"""Post tweet message to account."""
	try:
		twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret)
		twitter.update_status(status = message)
	except TwythonError as e:
		print(e)

def read_rss_and_tweet(url):
	"""Read RSS and post tweet."""
	feed = feedparser.parse(url)
	if feed:
		for item in feed["items"]:
			link = item["link"]
			if is_in_logfile(link, Settings.PostedUrlsOutputFile):
				print("Already posted:", link)
			else:
				post_tweet(message = compose_message(item))
				write_to_logfile(link, Settings.PostedUrlsOutputFile)
				print("Posted:", link)
	else:
		print("Nothing found in feed", url)

def get_query():
	"""Create Twitter search query with included words minus the excluded words."""
	include = " OR ".join(Settings.RetweetIncludeWords)
	exclude = " -".join(Settings.RetweetExcludeWords)
	return include + exclude

def search_and_retweet(query, count=10):
	"""Search for a query in tweets, and retweet those tweets."""
	try:
		twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret)
		search_results = twitter.search(q=query, count=count)
	except TwythonError as e:
		print(e)
	for tweet in search_results["statuses"]:
		# Make sure we don't retweet any dubplicates.
		if not is_in_logfile(tweet["id_str"], Settings.PostedRetweetsOutputFile):
			try:
				twitter.retweet(id = tweet["id_str"])
				write_to_logfile(tweet["id_str"], Settings.PostedRetweetsOutputFile)				
				print("Retweeted {} (id {})".format(shorten_text(tweet["text"], maxlength=40), tweet["id_str"]))
			except TwythonError as e:
				print(e)
		else:
			print("Already retweeted {} (id {})".format(shorten_text(tweet["text"], maxlength=40), tweet["id_str"]))

def is_in_logfile(content, filename):
	"""Does the content exist on any line in the log file?"""
	if os.path.isfile(filename):
		with open(filename) as f:
			lines = f.readlines()
		if (content + "\n" or content) in lines:
			return True
	return False
	
def write_to_logfile(content, filename):
	"""Append content to log file, on one line."""
	try:
		with open(filename, "a") as f:
			f.write(content + "\n")
	except IOError as e:
		print(e)

def display_help():
	"""Show available commands."""
	print("Syntax: python {} [command]".format(sys.argv[0]))
	print()
	print(" Commands:")
	print("    rss    Read URL and post new items to Twitter account (change account in source code)")
	print("    rt     Search and retweet keywords (see source code for keywords)")
	print("    help   Show this help screen")

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1].lower() == "rss":
			read_rss_and_tweet(url=Settings.FeedUrl)
		elif sys.argv[1].lower() == "rt":
			search_and_retweet(query=get_query())
		else:
			display_help()
	else:
		display_help()
