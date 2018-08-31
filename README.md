# Twitterbot

Twitterbot is a simple Python application for:

* reading and parsing a RSS feed and posting its title and links to a Twitter account.
* searching tweets for keywords or hashtags and retweet those tweets.

Both functions (Reading RSS and retweeting) can be used independently. The bot is limited to handle one feed and one Twitter account.

## Install

1. Download or git clone Twitterbot:
   - `git clone https://github.com/peterdalle/twitterbot`
2. Install dependencies [feedparser](https://pythonhosted.org/feedparser/) and [twython](https://twython.readthedocs.org/en/latest/):
   - `pip install feedparser`
   - `pip install twython`
3. Create a [Twitter application](https://apps.twitter.com/), and generate keys, tokens etc.
4. Modifiy the settings in the source code.
   - Modify `FeedUrl` to the RSS feed you want to read.
   - Modify the variables in the `TwitterAuth` class and add keys, tokens etc. for connecting to your Twitter app.
   - Modify `RetweetIncludeWords` for keywords you want to search and retweet, and `RetweetExcludeWords` for keywords you would like to exclude from retweeting. For example `RetweetIncludeWords = ["foo"]` and `RetweetExcludeWords = ["bar"]` will include any tweet with the word "foo", as long as the word "bar" is absent. This list can also be left empty, i.e. `RetweetExcludeWords = []`.

## Usage

Read the RSS feed and post to Twitter account:

```bash
$ python twitterbot.py rss
```

Search for tweets and retweet them:

```bash
$ python twitterbot.py rt
```

## Setup crontabs examples

Preferably, you should use crontab to set up Twitterbot to run on a schedule.

crontab examples:

```bash
# Read RSS feed every hour and tweet new links.
00 * * * * python twitterbot.py rss

# Rewteet keywords/hashtags every 15 minutes.
*/15 * * * * python twitterbot.py rt
```

Use the [cron schedule expression editor](https://crontab.guru/) to easily create crons.


## Questions

### How do I retweet a specific user?

Use the [Twitter search operators](https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators).

For example, search for user account `@soccerfan`:

```py 
RetweetIncludeWords = ["from:soccerfan"]
```

Search for hashtag `#football` from user account `@soccerfan`:

```py 
RetweetIncludeWords = ["#football+from:soccerfan"]
```

### How do I post the description instead of the title?

Modify the `ReadRssAndTweet()` method and use `item["description"]` for title instead, like so:

```py
# Read RSS and post tweet.
def ReadRssAndTweet(url):
	feed = feedparser.parse(url)
	for item in feed["items"]:
		title = item["description"]   # <--------------- Modify this line.
		link = item["link"]
		# Make sure we don't post any dubplicates.
		if not (IsUrlAlreadyPosted(link)):
			PostTweet(title, link)
			MarkUrlAsPosted(link)
			print("Posted: " + link)
		else:
			print("Already posted: " + link)
```
