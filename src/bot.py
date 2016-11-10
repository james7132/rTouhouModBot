import logging
import sys
import re
import time
from praw import *
from praw.objects import *
from datetime import datetime, timedelta
from model import *
from util import *
from urllib.parse import urlparse

logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

fh = logging.FileHandler('/var/log/rtouhoumod/bot.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

target_subreddit = "touhou"
owner = "james7132"
remove = False
credentials = load_json("./credentials.json")

limits = {
    timedelta(days=1): 1,
    timedelta(days=7): 4
}

# A list of flairs that are not image rehosts
flair_whitelist = load_regex_list("./flair_whitelist.txt")
# A list of flairs that are sure to be image rehosts
flair_blacklist = load_regex_list("./flair_blacklist.txt")

# A list of domains that are whitelisted as OC
domain_whitelist = load_regex_list("./domain_whitelist.txt")
# A list of domains that are sure to be image rehosts
domain_blacklist = load_regex_list("./domain_blacklist.txt")

session = Session()


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
    hostname = urlparse(url).hostname
    if(check_list(hostname, domain_blacklist)):
        return Decision.invalid_source
    return flair_result


def check_post(post):
    if post.banned_by is not None:
        return Decision.removed
    if post.is_self:
        return Decision.other
    flair = post.link_flair_text
    flair_check = check_flair(flair)
    if flair_check is not Decision.found_fanart:
        return flair_check
    # flair_check assumed to be false here
    return check_domain(post.url, flair_check)


def process_post(post, db_post, log, log_check=None):
    db_post.id = post.id
    db_post.date = datetime.fromtimestamp(post.created)
    old_status = db_post.status
    db_post.status = check_post(post)
    if log_check is None or old_status != db_post.status:
        logger.info(("%s: {"
                     "Flair: \"%s\" "
                     "Url Domain: \"%s\" "
                     "Post Type: %s "
                     "Before: %s}") % (log,
                                      post.link_flair_text,
                                      urlparse(post.url).hostname,
                                      db_post.status,
                                      old_status))
    if db_post.reported or db_post.status == old_status:
         return
    if db_post.status == Decision.invalid_source:
        if remove:
            post.add_comment(("This post has been deemed to be improperly sourcing"
                              " the posted material and will be removed."))
            post.remove()
            db_post.status = Decision.removed
        else:
            post.report("Invalid Sourcing.")
            logger.info("Reported post \"%s\" for invalid sourcing" %
                        db_post.id)
        db_post.reported =  True
    elif db_post.status == Decision.found_fanart:
        author = post.author.id
        for timespan, limit_count in limits.items():
            final_date = db_post.date
            initial_date = db_post.date - timespan
            count = session.query(Post) \
                .filter_by(status=Decision.found_fanart) \
                .filter_by(author_id=author) \
                .filter(Post.date.between(initial_date, final_date)).count()
            logger.info("%s has posted %s fanart posts in the last %s" %
                        (post.author, count, timespan))
            if limit_count < count:
                if remove:
                    post.add_comment(("The author of this post has posted more"
                                      " than %s found fanart posts in the last %s "
                                      " the posted material and will be removed.") %
                                     (limit_count, timespan))
                    post.remove()
                    db_post.status = Decision.removed
                else:
                    post.report("More than %s found fanart posts in the last %s"
                                % (limit_count, timespan))
                    logger.info(
                        "Reported post \"%s\" for exceeding time limits" % db_post.id)
                db_post.reported = True
                break
    session.commit()


def main_loop():
    #TODO(james7132): Switch to OAuth2 based authentication
    reddit = Reddit('/r/%s moderator written by /u/%sin PRAW' %
                    (target_subreddit, owner))
    reddit.login(username=credentials.username,
                 password=credentials.password,
                 log_requests=1,
                 disable_warning=True)
    logger.info('Logged in')
    subreddit = reddit.get_subreddit(target_subreddit)
    logger.info('Subreddit: {0}'.format(subreddit))
    longest_period = max(limits.keys()) * 2
    while True:
        for post in subreddit.get_new():
            db_post = session.query(Post).filter_by(id=post.id).first()
            if db_post is not None:
                continue
            author_id = post.author.id
            author = session.query(User).filter_by(id=author_id).first()
            if author is None:
                author = User(id=author_id)
                session.add(author)
            db_post = Post()
            author.posts.append(db_post)
            process_post(post,
                         db_post,
                         "New Post")
            session.commit()
        now = datetime.now()
        back = now - longest_period
        for db_post in session.query(Post).filter(
                Post.date.between(back, now)).all():
            post = reddit.get_info(thing_id="t3_" + db_post.id)
            process_post(post,
                         db_post,
                         "Updated Post",
                         lambda p, dp: dp.status != Decision.watch)
        time.sleep(10)


def main():
    logger.info("Flair Whitelist: %s", [
                regex.pattern for regex in flair_whitelist])
    logger.info("Fliar Blacklist: %s", [
                regex.pattern for regex in flair_blacklist])

    logger.info("Domain Whitelist: %s", [
                regex.pattern for regex in domain_whitelist])
    logger.info("Domain Blacklist: %s", [
                regex.pattern for regex in domain_blacklist])

    while True:
        try:
            main_loop()
        except KeyboardInterrupt:
            log.info('KeyboardInterrupt recieved, shutting down')
            break
        except Exception as e:
            logger.error(str(e))

if __name__ == "__main__":
    main()
