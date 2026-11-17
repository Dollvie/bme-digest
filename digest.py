# Daily UCI BME news digest
# Reads RSS feeds, keeps recent stories, and writes them to bme_digest.txt
# (an empty file means no new stories, so no notification is sent).

import feedparser
from calendar import timegm
from datetime import datetime, timedelta, timezone

# Feeds covering the whole campus: stories must match a keyword below.
SITE_FEEDS = [
    "https://news.uci.edu/feed/",
]

# Google News searches: Google already does the matching, so no keyword
# filter is applied. Build more at news.google.com/rss/search?q=YOUR+QUERY
# (use + for spaces and %22 for quote marks; when:7d limits to the past week).
SEARCH_FEEDS = []

KEYWORDS = [
    "biomedical",
    "bioengineering",
    "bioengineer",
    "bme",
    "tissue engineering",
    "biomaterials",
    "medical device",
    "regenerative",
    "biosensor",
    "samueli school of engineering",
]

DAYS_BACK = 7

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
seen_links = set()
seen_titles = set()
stories = []


def collect(url, use_keywords):
    feed = feedparser.parse(url)
    print(f"{url[:70]}...: {len(feed.entries)} entries found")
    if feed.bozo and not feed.entries:
        print(f"  Warning: could not read this feed ({feed.get('bozo_exception')})")
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
            if not any(k in text for k in KEYWORDS):
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
