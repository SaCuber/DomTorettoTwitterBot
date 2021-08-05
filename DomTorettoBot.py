import tweepy
import json
import time
import random

with open("auth.json", "r") as f:
    credentials = json.load(f)

consumer_key = credentials["ck"]
consumer_secret = credentials["cs"]
access_token = ""
access_secret = ""

with open("filtered_terms.txt", "r") as f:
    filtered_terms = f.read().splitlines()

answers = [
    "Did I hear someone say Family? Nothing's more important than family!",
    "Did someone say Family? Family's the most important thing!",
    "Family? Nothing's more important than family!"
]

with open("tweets.txt", "r") as f:
    replied = f.read().splitlines()

recent_replies = []

with open("user_blacklist.txt", "r") as f:
    blacklist = f.read().splitlines()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret, "oob")

def filter(text):
    r = True
    text = text.lower()
    for term in filtered_terms:
        if term in text:
            r = False
    return r

def get_access():
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')

    request_token = auth.request_token['oauth_token']

    print(redirect_url)

    verifier = input("Verifier: ")

    auth.request_token = { 'oauth_token' : request_token, 'oauth_token_secret' : verifier }

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')
    else:
        credentials["at"] = auth.access_token
        credentials["as"] = auth.access_token_secret
        print("Access granted let's go poggers moment")

if credentials["at"] and credentials["as"]:
    access_token, access_secret = credentials["at"], credentials["as"]
    auth.set_access_token(access_token, access_secret)
    print("I'm in, boss")
else:
    get_access()
    with open("auth.json", "w") as f:
        f = json.dump(credentials, f, indent=4)

api = tweepy.API(auth)

print(f"\n[{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}]Starting...\n")
try:
    while True:
        tweets = api.search("family", count=1, result_type="recent")
        for tweet in tweets:
            text = tweet.text
            if "family" in text.lower() and filter(text):
                if not tweet.id_str in replied and not tweet.user.id_str in blacklist:
                    print(f"\n[{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}] Tweet found: {text}")
                    print(f'Tweet by {tweet.user.screen_name}')
                    print(f'Responding...')
                    try:
                        api.update_status(status=answers[random.randint(0, 2)], in_reply_to_status_id = tweet.id, auto_populate_reply_metadata=True)
                        print("Responded")
                    except Exception as e:
                        print(e)
                    replied.append(tweet.id_str)
                    recent_replies.append(tweet.id_str)
                    print("Waiting 30 minutes...\n")
                    time.sleep(1800)
except KeyboardInterrupt:
    print("\n\nShutting Down")
    with open("tweets.txt", "a") as f:
        for i in recent_replies:
            f.write(f"\n{i}")
    print("Stored Reply ids")
    print("Stopping...")
    quit()
except Exception as e:
    print(f"[{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}] An Exception Ocurred: {e}")    
