import praw
import time
from model import * 
from util import *
from urllib.parse import urlparse

credentials = load_json("./credentials.json")

# A list of flairs that are not image rehosts
flair_whitelist = load_list("./flair_whitelist.txt")
# A list of flairs that are sure to be image rehosts
flair_blacklist = load_list("./flair_blacklist.txt")

# A list of domains that are whitelisted as OC
domain_whitelist = load_list("./domain_whitelist.txt")
# A list of domains that are sure to be image rehosts
domain_blacklist = load_list("./domain_blacklist.txt")

def main():
    #TODO(james7132): Switch to proper logging
    print("Flair Whitelist: ", flair_whitelist)
    print("Fliar Blacklist: ", flair_blacklist)

    print("Domain Whitelist: ", domain_whitelist)
    print("Domain Blacklist: ", domain_blacklist)

    #TODO(james7132): Switch to OAuth2 based authentication
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
