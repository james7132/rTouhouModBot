import praw
import time
import json
from collections import namedtuple
from urllib.parse import urlparse

def load_list(filename):
    with open(filename, 'r') as target_file:
        return set(s.replace('\n', '') for s in target_file)

def convert(name, dictionary):
    return namedtuple(name, dictionary.keys())(**dictionary)

def load_json(filename):
    with open(filename, 'r') as target_file:
        return convert("json", json.load(target_file))

credentials = load_json("./credentials.json")

# A list of flairs that are not image rehosts
flair_whitelist = load_list("./flair_whitelist.txt")
# A list of flairs that are sure to be image rehosts
flair_blacklist = load_list("./flair_blacklist.txt")

# A list of domains that are whitelisted as OC
domain_whitelist = load_list("./domain_whitelist.txt")
# A list of domains that are sure to be image rehosts
domain_blacklist = load_list("./domain_blacklist.txt")

print("Domain Whitelist: ", domain_whitelist)
print("Domain Blacklist: ", domain_blacklist)

def main():
    reddit = praw.Reddit('/r/touhou moderator written by /u/james7132 in PRAW')
    reddit.login(username=credentials.username,
            password=credentials.password,disable_warning=True)
    print('Logged in')
    subreddit = reddit.get_subreddit('touhou')
    print('Subreddit: {0}'.format(subreddit))
    while True:
        for submission in subreddit.get_new():
            url = urlparse(submission.url)
            if(submission.link_flair_text is not None):
                print(submission.link_flair_text,url.hostname)
        time.sleep(60)

if __name__ == "__main__":
    main()
