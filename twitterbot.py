#!/usr/bin/python
# -*- coding: utf-8 -*-

# Get RSS feed items from http://example.net/feed/ and post tweets to @youraccount.
# By Peter M. Dahlgren, @peterdalle

from twython import Twython, TwythonError
import csv
import sys
import os
import re
import time
import datetime
import feedparser
from datetime import date

# Settings for the application.
class Settings:
	FeedUrl = "http://example.net/feed/"			# RSS feed to read and post tweets from.
	PostedUrlsOutputFile = "posted-urls.log"		# Log file to save all tweeted RSS links (one URL per line).
	PostedRetweetsOutputFile = "posted-retweets.log"	# Log file to save all retweeted tweets (one tweetid per line).

# Twitter authentication settings. Create a Twitter app at https://apps.twitter.com/ and
# generate key, secret etc, and insert them below.
class TwitterAuth:
	ConsumerKey = "XXX"
	ConsumerSecret = "XXX"
	AccessToken = "XXX"
	AccessTokenSecret = "XXX"

# Post tweet to account.
def PostTweet(title, link):
	# Truncate title and append ... at the end if length exceeds 113 chars.
	title = (title[:113] + '...') if len(title) > 113 else title
	message = title + " " + link
	try:
		# Tweet message.
		twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret) # Connect to Twitter.
		twitter.update_status(status = message)
	except TwythonError as e:
		print(e)

# Read RSS and post tweet.
def ReadRssAndTweet(url):
	feed = feedparser.parse(url)
	for item in feed["items"]:
		title = item["title"]
		link = item["link"]
		# Make sure we don't post any dubplicates.
		if not (IsUrlAlreadyPosted(link)):
			PostTweet(title, link)
			MarkUrlAsPosted(link)
			print("Posted: " + link)
		else:
			print("Already posted: " + link)
			
# Has the URL already been posted? 
def IsUrlAlreadyPosted(url):
	if os.path.isfile(Settings.PostedUrlsOutputFile):
		# Check whether URL is in log file.
		f = open(Settings.PostedUrlsOutputFile)
		posted_urls = f.readlines()
		f.close()
		if (url + "\n" or url) in posted_urls:
			return(True)
		else:
			return(False)
	else:
		return(False)

# Mark the specific URL as already posted.
def MarkUrlAsPosted(url):
	try:
		# Write URL to log file.
		f = open(Settings.PostedUrlsOutputFile, "a")
		f.write(url + "\n")
		f.close()
	except:
		print("Write error:", sys.exc_info()[0])

# Search for particular keywords in tweets and retweet those tweets.
def SearchAndRetweet():
	exclude_words = [] 		# Do not include tweets with these words.
	include_words = ["#hashtag"]	# Include tweets with these words.

	# Create Twitter search query with included words minus the excluded words.
	filter = " OR ".join(include_words)
	blacklist = " -".join(exclude_words)
	keywords = filter + blacklist

	# Connect to Twitter.
	twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret)
	search_results = twitter.search(q=keywords, count=10)
	try:
		for tweet in search_results["statuses"]:
			# Make sure we don't retweet any dubplicates.
			if not IsTweetAlreadyRetweeted(tweet["id_str"]):
				try:
					twitter.retweet(id = tweet["id_str"])
					MarkTweetAsRetweeted(tweet["id_str"])
					print("Retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")
				except TwythonError as e:
					print(e)
			else:
				print("Already retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")
	except TwythonError as e:
		print(e)

# Has the tweet already been retweeted? 
def IsTweetAlreadyRetweeted(tweetid):
	if os.path.isfile(Settings.PostedRetweetsOutputFile):
		# Check whether tweet IDs is in log file.
		f = open(Settings.PostedRetweetsOutputFile)
		posted_tweets = f.readlines()
		f.close()
		if (tweetid + "\n" or tweetid) in posted_tweets:
			return(True)
		else:
			return(False)
	else:
		return(False)

# Mark the specific tweet as already retweeted.
def MarkTweetAsRetweeted(tweetid):
	try:
		# Write tweet ID to log file.
		f = open(Settings.PostedRetweetsOutputFile, "a")
		f.write(tweetid + "\n")
		f.close()
	except:
		print("Write error:", sys.exc_info()[0])

# Show available commands.
def DisplayHelp():
	print("Syntax: python twitterbot.py [cmd]")
	print
	print(" Available commands:")
	print("    rss    Read URL and post new items to Twitter account (change account in source code)")
	print("    rt     Search and retweet keywords (see source code for keywords)")
	print("    help   Show this help screen")
	print

# Main.
if (__name__ == "__main__"):
	if len(sys.argv) > 1:
		cmd = sys.argv[1]
		if (cmd == "rss"):
			ReadRssAndTweet(Settings.FeedUrl)
		elif (cmd == "rt"):
			SearchAndRetweet()
		else:
			DisplayHelp()
	else:
		DisplayHelp()
		sys.exit()
