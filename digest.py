# Daily UCI BME news digest
# Reads RSS feeds, keeps recent stories that match your keywords,
# and writes them to bme_digest.txt (empty file = no new stories).

import feedparser
from calendar import timegm
from datetime import datetime, timedelta, timezone

# Add any other feed URLs you confirm work (open them in a browser first).
FEEDS = [
    "https://news.uci.edu/feed/",
]

KEYWORDS = [
    "biomedical engineering",
    "bme",
    "bioengineering",
    "samueli school of engineering",
]

DAYS_BACK = 7  # BME news is sparse, so look back a week

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
seen = set()
stories = []

for url in FEEDS:
    feed = feedparser.parse(url)
    print(f"{url}: {len(feed.entries)} entries found")
    if feed.bozo and not feed.entries:
        print(f"  Warning: could not read this feed ({feed.get('bozo_exception')})")
        continue
    for e in feed.entries:
        if not e.get("published_parsed") or e.link in seen:
            continue
        when = datetime.fromtimestamp(timegm(e.published_parsed), timezone.utc)
        text = (e.title + " " + e.get("summary", "")).lower()
        if when > cutoff and any(k in text for k in KEYWORDS):
            seen.add(e.link)
            stories.append((when, e.title, e.link))

stories.sort(reverse=True)

with open("bme_digest.txt", "w", encoding="utf-8") as f:
    for when, title, link in stories:
        f.write(f"{when:%b %d} - {title}\n{link}\n\n")

print(f"{len(stories)} matching stories written to bme_digest.txt")
