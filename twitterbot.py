#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import feedparser
from twython import Twython, TwythonError


class Settings:
    """Twitter bot application settings.

    Enter the RSS feed you want to tweet, or keywords you want to retweet.
    """
    # RSS feed to read and post tweets from.
    feed_url = "http://example.net/feed/"

    # Log file to save all tweeted RSS links (one URL per line).
    posted_urls_output_file = "posted-urls.log"

    # Log file to save all retweeted tweets (one tweetid per line).
    posted_retweets_output_file = "posted-retweets.log"

    # Include tweets with these words when retweeting.
    retweet_include_words = ["#hashtag"]

    # Do not include tweets with these words when retweeting.
    retweet_exclude_words = []


class TwitterAuth:
    """Twitter authentication settings.

    Create a Twitter app at https://apps.twitter.com/ and generate
    consumer key, consumer secret etc. and insert them here.
    """
    consumer_key = "XXX"
    consumer_secret = "XXX"
    access_token = "XXX"
    access_token_secret = "XXX"


def compose_message(item: feedparser.FeedParserDict) -> str:
    """Compose a tweet from an RSS item (title, link, description)
    and return final tweet message.

    Parameters
    ----------
    item: feedparser.FeedParserDict
        An RSS item.

    Returns
    -------
    str
        Returns a message suited for a Twitter status update.
    """
    title, link, _ = item["title"], item["link"], item["description"]
    message = shorten_text(title, maxlength=250) + " " + link
    return message


def shorten_text(text: str, maxlength: int) -> str:
    """Truncate text and append three dots (...) at the end if length exceeds
    maxlength chars.

    Parameters
    ----------
    text: str
        The text you want to shorten.
    maxlength: int
        The maximum character length of the text string.

    Returns
    -------
    str
        Returns a shortened text string.
    """
    return (text[:maxlength] + '...') if len(text) > maxlength else text


def post_tweet(message: str):
    """Post tweet message to account.

    Parameters
    ----------
    message: str
        Message to post on Twitter.
    """
    try:
        twitter = Twython(TwitterAuth.consumer_key,
                          TwitterAuth.consumer_secret,
                          TwitterAuth.access_token,
                          TwitterAuth.access_token_secret)
        twitter.update_status(status=message)
    except TwythonError as e:
        print(e)


def read_rss_and_tweet(url: str):
    """Read RSS and post feed items as a tweet.

    Parameters
    ----------
    url: str
        URL to RSS feed.
    """
    feed = feedparser.parse(url)
    if feed:
        for item in feed["items"]:
            link = item["link"]
            if is_in_logfile(link, Settings.posted_urls_output_file):
                print("Already posted:", link)
            else:
                post_tweet(message=compose_message(item))
                write_to_logfile(link, Settings.posted_urls_output_file)
                print("Posted:", link)
    else:
        print("Nothing found in feed", url)


def get_query() -> str:
    """Create Twitter search query with included words minus the
    excluded words.

    Returns
    -------
    str
        Returns a string with the Twitter search query.
    """
    include = " OR ".join(Settings.retweet_include_words)
    exclude = " -".join(Settings.retweet_exclude_words)
    exclude = "-" + exclude if exclude else ""
    return include + " " + exclude


def search_and_retweet(query: str, count=10):
    """Search for a query in tweets, and retweet those tweets.

    Parameters
    ----------
    query: str
        A query to search for on Twitter.
    count: int
        Number of tweets to search for. You should probably keep this low
        when you use search_and_retweet() on a schedule (e.g. cronjob).
    """
    try:
        twitter = Twython(TwitterAuth.consumer_key,
                          TwitterAuth.consumer_secret,
                          TwitterAuth.access_token,
                          TwitterAuth.access_token_secret)
        search_results = twitter.search(q=query, count=count)
    except TwythonError as e:
        print(e)
        return
    for tweet in search_results["statuses"]:
        # Make sure we don't retweet any dubplicates.
        if not is_in_logfile(
                    tweet["id_str"], Settings.posted_retweets_output_file):
            try:
                twitter.retweet(id=tweet["id_str"])
                write_to_logfile(
                    tweet["id_str"], Settings.posted_retweets_output_file)
                print("Retweeted {} (id {})".format(shorten_text(
                    tweet["text"], maxlength=40), tweet["id_str"]))
            except TwythonError as e:
                print(e)
        else:
            print("Already retweeted {} (id {})".format(
                shorten_text(tweet["text"], maxlength=40), tweet["id_str"]))


def is_in_logfile(content: str, filename: str) -> bool:
    """Does the content exist on any line in the log file?

    Parameters
    ----------
    content: str
        Content to search file for.
    filename: str
        Full path to file to search.

    Returns
    -------
    bool
        Returns `True` if content is found in file, otherwise `False`.
    """
    if os.path.isfile(filename):
        with open(filename) as f:
            lines = f.readlines()
        if (content + "\n" or content) in lines:
            return True
    return False


def write_to_logfile(content: str, filename: str):
    """Append content to log file, on one line.

    Parameters
    ----------
    content: str
        Content to append to file.
    filename: str
        Full path to file that should be appended.
    """
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
    print("    rss    Read URL and post new items to Twitter")
    print("    rt     Search and retweet keywords")
    print("    help   Show this help screen")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "rss":
            read_rss_and_tweet(url=Settings.feed_url)
        elif sys.argv[1].lower() == "rt":
            search_and_retweet(query=get_query())
        else:
            display_help()
    else:
        display_help()
