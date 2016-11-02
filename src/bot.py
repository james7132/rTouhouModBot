import logging
import sys
import praw
import re
import time
from datetime import datetime
from model import * 
from util import *
from urllib.parse import urlparse

logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)

credentials = load_json("./credentials.json")

# A list of flairs that are not image rehosts
flair_whitelist = load_regex_list("./flair_whitelist.txt")
# A list of flairs that are sure to be image rehosts
flair_blacklist = load_regex_list("./flair_blacklist.txt")

# A list of domains that are whitelisted as OC
domain_whitelist = load_regex_list("./domain_whitelist.txt")
# A list of domains that are sure to be image rehosts
domain_blacklist = load_regex_list("./domain_blacklist.txt")

def check_list(check, regex_list):
    return any(pattern.match(check) for pattern in regex_list)

def check_flair(flair):
    if flair is None:
        return Decision.watch 
    if(check_list(flair, flair_whitelist)):
        return Decision.original_content
    elif(check_list(flair, flair_blacklist)):
        return Decision.found_fanart
    return Decision.other

def check_domain(url, flair_result):
    hostname = urlparse(url).hostname;
    if(check_list(hostname, domain_blacklist)):
        return Decision.invalid_source
    return flair_result

def check_post(is_self, flair, url):
    if is_self:
        return Decision.other
    flair_check = check_flair(flair)
    if flair_check is not Decision.found_fanart:
        return flair_check
    # flair_check assumed to be false here
    return check_domain(url, flair_check)

def main():
    logger.info("Flair Whitelist: %s", [regex.pattern for regex in flair_whitelist])
    logger.info("Fliar Blacklist: %s", [regex.pattern for regex in flair_blacklist])

    logger.info("Domain Whitelist: %s", [regex.pattern for regex in domain_whitelist ])
    logger.info("Domain Blacklist: %s", [regex.pattern for regex in domain_blacklist ])

    #TODO(james7132): Switch to OAuth2 based authentication
    reddit = praw.Reddit('/r/touhou moderator written by /u/james7132 in PRAW')
    reddit.login(username=credentials.username,
            password=credentials.password,
            log_requests=1,
            disable_warning=True)
    logger.info('Logged in')
    subreddit = reddit.get_subreddit('james7132')
    logger.info('Subreddit: {0}'.format(subreddit))
    session = Session()
    while True:
        for post in subreddit.get_new():
            db_post = session.query(Post).filter_by(id = post.id).first()
            if db_post is not None and db_post.status != Decision.watch:
                continue
            author_id = post.author.id
            author = session.query(User).filter_by(id = author_id).first()
            if author is None:
                author = User(id = author_id)
                session.add(author)
            if db_post is None:
                db_post = Post()
                author.posts.append(db_post)
            flair = post.link_flair_text
            url = post.url
            db_post.id = post.id
            db_post.date = datetime.fromtimestamp(post.created)
            db_post.status = check_post(post.is_self, flair, url)
            logger.info(("New Post: {"
                         "Flair: \"%s\" "
                         "Url Domain \"%s\" "
                         "Post Check %s}") % (flair, 
                        urlparse(url).hostname,
                        db_post.status))
            session.commit()
        time.sleep(10)

if __name__ == "__main__":
    main()
