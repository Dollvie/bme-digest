# Daily UCI BME news digest
# Reads RSS feeds, keeps recent stories, and writes them to bme_digest.txt
# (an empty file means no new stories, so no notification is sent).

import feedparser
from calendar import timegm
from datetime import datetime, timedelta, timezone

# Campus-wide feeds: a story is kept only if it matches a keyword or name below.
SITE_FEEDS = [
    "https://news.uci.edu/feed/", "https://news.google.com/home?hl=en-US&gl=US&ceid=US:en"
]

# Feeds where everything is relevant (student orgs, publication searches).
# No keyword check is applied. If a feed doesn't work, the run log shows a
# warning and the script carries on with the others.
SEARCH_FEEDS = ["https://pubmed.ncbi.nlm.nih.gov/rss/search/1Ds1JEbG0OW5BdrY4sRlHbcspN3vr7h4LWMc_03mZ2C8HY5QMY/?limit=100&utm_campaign=pubmed-2&fc=20261116200730"]

KEYWORDS = [
    "biomedical",
    "bioengineering",
    "bioengineer",
    "bme",
    "BME",
    "BMES",
    "bmes",
    "gabes",
    "GABES",
    "tissue engineering",
    "biomaterials",
    "medical device",
    "regenerative",
    "biosensor",
    "samueli school of engineering",
]

# UCI BME faculty (from the department's faculty page). Full names are used
# so common surnames like Lee or Liu don't cause false matches.
FACULTY = [
    "Michelle Digman", "Kyriacos Athanasiou", "Elliot Botvinick",
    "Gregory Brewer", "James Brody", "Zhongping Chen", "Naomi Chesler",
    "Bernard Choi", "Fangyuan Ding", "Tim Downing", "Enrico Gratton",
    "Anna Grosberg", "Jered Haun", "Elliot Hui", "Tibor Juhasz",
    "Arash Kheradvar", "Michelle Khine", "Christine King", "Abraham Lee",
    "Chang Liu", "Wendy Liu", "Beth Lopour", "Joshua Mauney",
    "Zoran Nenadic", "Ronke Olabisi", "Pim Oomen", "Daryl Preece",
    "Gurneet Sangha", "William Tang", "Bruce Tromberg", "Liangzhong Xiang",
]

MATCH_TERMS = [k.lower() for k in KEYWORDS + FACULTY]

DAYS_BACK = 7   # how many days back to look

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
seen_links = set()
seen_titles = set()
stories = []


def collect(url, use_keywords):
    feed = feedparser.parse(url)
    print(f"{url[:70]}...: {len(feed.entries)} entries found")
    if not feed.entries:
        print("  Warning: no entries (the feed may not exist or may be empty)")
        return
    for e in feed.entries:
        if not e.get("published_parsed"):
            continue
        if e.link in seen_links or e.title.lower() in seen_titles:
            continue
        when = datetime.fromtimestamp(timegm(e.published_parsed), timezone.utc)
        if when <= cutoff:
            continue
        if use_keywords:
            text = (e.title + " " + e.get("summary", "")).lower()
            if not any(k in text for k in MATCH_TERMS):
                continue
        seen_links.add(e.link)
        seen_titles.add(e.title.lower())
        stories.append((when, e.title, e.link))


for url in SITE_FEEDS:
    collect(url, use_keywords=True)
for url in SEARCH_FEEDS:
    collect(url, use_keywords=False)

stories.sort(reverse=True)

with open("bme_digest.txt", "w", encoding="utf-8") as f:
    for when, title, link in stories:
        f.write(f"{when:%b %d} - {title}\n{link}\n\n")

print(f"{len(stories)} matching stories written to bme_digest.txt")
