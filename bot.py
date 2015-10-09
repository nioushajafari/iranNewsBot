import codecs
import HTMLParser
import os
import urllib2
import tweepy
from time import gmtime, strftime
from secrets import *
from bs4 import BeautifulSoup

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
hparser = HTMLParser.HTMLParser()

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
api = tweepy.API(auth)
tweets = api.user_timeline('IranNewsBot')


# ====== Individual bot configuration ==========================
bot_username = 'IranNewsBot'
logfile_name = bot_username + ".log"


# ==============================================================


def get():
    # Get the headlines, iterate through them to try to find a suitable one
    page = 1
    while page <= 3:
        try:
            request = urllib2.Request(
                "http://content.guardianapis.com/search?format=json&page-size=50&page=" +
                str(page) + "&api-key=" + GUARDIAN_KEY)
            response = urllib2.urlopen(request)
            print("got the response")

        except urllib2.URLError as e:
            print(e.reason)

        else:
            print("we're in else")
            html = BeautifulSoup(response.read(), "lxml")
            items = html.find_all('item')
            for item in items:
                print("in the items")
                print(item)
                headline = item.title.string
                h_split = headline.split()

                # We don't want to use incomplete headlines
                if "..." in headline:
                    continue

                # Try to weed out all-caps headlines
                if count_caps(h_split) >= len(h_split) - 3:
                    continue

                # Remove attribution string
                if "-" in headline:
                    headline = headline.split("-")[:-1]
                    headline = ' '.join(headline).strip()

                if process(headline):
                    break

                else:
                    page += 1

        page += 1

    # Log that no tweet could be made
    f = open(os.path.join(__location__, "IranNewsBot.log"), 'a')
    t = strftime("%d %b %Y %H:%M:%S", gmtime())
    f.write("\n" + t + " No possible tweet.")
    f.close()


def process(headline):
    headline = hparser.unescape(headline).strip()

    print("processing")
    # Don't tweet anything that's too long
    if len(headline) > 140:
        return False


    # Don't tweet anything Iran isn't mentioned in
    if "a" not in headline:
        print("didn't find a")
        return False

    else:
        print("off to tweet")
        return tweet(headline)


def tweet(headline):
    # Check that we haven't tweeted this before
    for tweet in tweets:
        if headline == tweet.text:
            return False

    # Log tweet to file
    f = codecs.open(os.path.join(__location__, "IranNewsBot.log"), 'a', encoding='utf-8')
    t = strftime("%d %b %Y %H:%M:%S", gmtime())
    f.write("\n" + t + " " + headline)
    f.close()

    # Post tweet
    api.update_status(headline)
    return True


def count_caps(headline):
    count = 0
    for word in headline:
        if word[0].isupper():
            count += 1
    return count


def log(message):
    """Log message to logfile."""
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)


if __name__ == "__main__":
    get()
