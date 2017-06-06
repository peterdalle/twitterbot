#!/usr/bin/python
# -*- coding: utf-8 -*-

# Get RSS feed items from http://medieforskarna.se/feed/ and post tweets to account @medieforskarna.
# Peter M. Dahlgren
# 2015-10-31, updated 2017-06-06 with truncate RSS feed title to fit into Twitter 140 chars

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
	FeedUrl = "http://medieforskarna.se/feed/"				# RSS feed to read and post tweets from.
	PostedUrlsOutputFile = "medieforskarna-posted-urls.log"			# Log file to save all tweeted RSS links (one URL per line).
	PostedRetweetsOutputFile = "medieforskarna-posted-retweets.log"		# Log file to save all retweeted tweets (one tweetid per line).


# Twitter authentication settings.
class TwitterAuth:
	# Create a Twitter app at https://apps.twitter.com/
	ConsumerKey = "XXX"
	ConsumerSecret = "XXX"
	AccessToken = "XXX"
	AccessTokenSecret = "XXX"


# Post tweet to account.
def PostTweet(title, link):
	title = (title[:113] + '...') if len(title) > 113 else title	# Truncate title and append ... at the end if length exceeds 113 chars.
	message = title + " " + link
	try:
		twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret) # Connect to Twitter.
		twitter.update_status(status = message) # Tweet message.
	except TwythonError as e:
		print(e)


# Read RSS and post.
def ReadRssAndTweet(url):
	feed = feedparser.parse(url)
	for item in feed["items"]:
		title = item["title"]
		link = item["link"]
		if not (IsUrlAlreadyPosted(link)): # Make sure we don't post any dubplicates.
			PostTweet(title, link)
			MarkUrlAsPosted(link)
			print("Posted: " + link)
		else:
			print("Already posted: " + link)

		# Debug:
		#print(message.encode("utf-8"))
		#time.sleep(1)


# Has the URL already been posted? 
def IsUrlAlreadyPosted(url):
	if os.path.isfile(Settings.PostedUrlsOutputFile):
		# Read log file and check whether URL is in the log file.
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
	exclude_words = [] 					# Do not include tweets with these words.
	include_words = ["#medieforskning"]			# Include tweets with these words.

	# Create Twitter search query with included words minus the excluded words.
	filter = " OR ".join(include_words)
	blacklist = " -".join(exclude_words)
	keywords = filter + blacklist

	twitter = Twython(TwitterAuth.ConsumerKey, TwitterAuth.ConsumerSecret, TwitterAuth.AccessToken, TwitterAuth.AccessTokenSecret) # Connect to Twitter.
	search_results = twitter.search(q=keywords, count=10)
	try:
		for tweet in search_results["statuses"]:
			if not IsTweetAlreadyRetweeted(tweet["id_str"]):	# Make sure we don't retweet any dubplicates.
				try:
					twitter.retweet(id = tweet["id_str"])
					MarkTweetAsRetweeted(tweet["id_str"])
					print("Retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")
				except TwythonError as e:
					print(e)
			else:
				print("Already retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")

			# Debug:
			#print(tweet["text"].encode("utf-8"))
			#time.sleep(1)
	except TwythonError as e:
		print(e)


# Has the tweet already been retweeted? 
def IsTweetAlreadyRetweeted(tweetid):
	if os.path.isfile(Settings.PostedRetweetsOutputFile):
		# Read log file and check whether the tweets ID is in the log file.
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
		# Write the tweets ID to log file.
		f = open(Settings.PostedRetweetsOutputFile, "a")
		f.write(tweetid + "\n")
		f.close()
	except:
		print("Write error:", sys.exc_info()[0])


# Show available commands.
def DisplayHelp():
	print("Syntax: python medieforskarna.py [cmd]")
	print
	print(" Available commands:")
	print("    rss    Read URL and post new items to @medieforskarna")
	print("    rt     Search and retweet #medieforskning")
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
