# /r/Touhou's Moderator Bot

The Touhou Subreddit has special rules regarding image posts made to the
subreddit. This bot was created to make it easier for the moderators to keep
track of users and their posts made to the subreddit. This reddit bot does the
following

0. Keep track of posts made to the subreddit on a daily and weekly basis.
0. Enforce daily limits on art posts on a per user basis.
0. Enforce weekly limits on art posts on a per user basis.
0. Ensure art posts are directly linking to the source instead of using
   rehosting services.

The bot operates based on the following data:

* The individual user creating posts.
* The time posts are created.
* The URL of the link posts.
* The applied flair on each individual post.

The end goal is to allow either users or mods to mark the flair on posts, and
let the bot handle the rest of the moderation with respect to these rules.

# How the bot determines posts to moderate

The bot has a blacklist and whitelist for both domains and flairs, applied in
the following priorities (lower priority precedes all following decisions):

0. Posts that meet the whitelist criteria on **either** whitelists are ignored 
   and are automatically exempt from moderation.
0. Posts that meet the flair blacklist are always subject to moderation.
0. Posts that meet the domain blacklist are only subject to moderation if not in
   the flair whitelist.
