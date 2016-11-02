import praw
import re
import time
from enum import Enum, unique
from model import * 
from util import *
from urllib.parse import urlparse

credentials = load_json("./credentials.json")

# A list of flairs that are not image rehosts
flair_whitelist = load_regex_list("./flair_whitelist.txt")
# A list of flairs that are sure to be image rehosts
flair_blacklist = load_regex_list("./flair_blacklist.txt")

# A list of domains that are whitelisted as OC
domain_whitelist = load_regex_list("./domain_whitelist.txt")
# A list of domains that are sure to be image rehosts
domain_blacklist = load_regex_list("./domain_blacklist.txt")

completed = set()
to_watch = list()

class Decision(Enum):
    other = 1               # this post is not subject to moderation
    watch = 2               # watch this post for further changes
    found_fanart = 3        # post is a piece of found fanart
    original_content = 4    # post is original content
    invalid_source = 5      # post is found fanart with improper sourcing

def check_list(check, regex_list):
    return any(pattern.match(check) for pattern in regex_list)

def check_flair(post):
    if post.link_flair_text is None:
        return Decision.watch 
    flair = post.link_flair_text
    if(check_list(flair, flair_whitelist)):
        return Decision.original_content
    elif(check_list(flair, flair_blacklist)):
        return Decision.found_fanart
    return Decision.other

def check_domain(post, flair_result):
    hostname = urlparse(post.url).hostname;
    if(check_list(hostname, domain_blacklist)):
        return Decision.invalid_source
    return flair_result

def check_post(post):
    url = urlparse(post.url)
    result = None 
    reason = None
    flair = post.link_flair_text

    flair_check = check_flair(post)
    if flair_check is not Decision.found_fanart:
        return flair_check

    # flair_check assumed to be false here
    return check_domain(post, flair_check)

def main():
    #TODO(james7132): Switch to proper logging
    print("Flair Whitelist: ", [regex.pattern for regex in flair_whitelist])
    print("Fliar Blacklist: ", [regex.pattern for regex in flair_blacklist])

    print("Domain Whitelist: ", [regex.pattern for regex in domain_whitelist ])
    print("Domain Blacklist: ", [regex.pattern for regex in domain_blacklist ])

    #TODO(james7132): Switch to OAuth2 based authentication
    reddit = praw.Reddit('/r/touhou moderator written by /u/james7132 in PRAW')
    reddit.login(username=credentials.username,
            password=credentials.password,disable_warning=True)
    print('Logged in')
    subreddit = reddit.get_subreddit('touhou')
    print('Subreddit: {0}'.format(subreddit))
    while True:
        for post in subreddit.get_new():
            if(post.id in completed):
                continue
            print(post.link_flair_text, urlparse(post.url).hostname,
                    check_post(post))
        time.sleep(60)

if __name__ == "__main__":
    main()
