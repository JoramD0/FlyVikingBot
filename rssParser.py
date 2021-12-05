import feedparser, re, time

async def read_feed(rss_url, pretty_name, callback):
# Read last modified and pull feed
    try:
        with open(f"{pretty_name}_rss_trackfile", "r") as trackfile:
            original_trackfile_time = trackfile.read()
            feed = feedparser.parse(rss_url, modified=original_trackfile_time)
    except:
        original_trackfile_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) # To prevent error on first run
        feed = feedparser.parse(rss_url)

    # Write latest modified if new feed
    if feed.status == 200:
        with open(f"{pretty_name}_rss_trackfile", "w") as trackfile:
            try:
                trackfile.write(feed.modified)
            except:
                trackfile.write(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime()))

        for entry in feed.entries:
            last_check = time.strptime(original_trackfile_time, "%a, %d %b %Y %H:%M:%S %Z")

            # Check if entry was posted since last check
            if time.mktime(entry.published_parsed) > time.mktime(last_check):
                result = re.search('src="([^"]+)"', entry.summary).group()
                if pretty_name == "gallery":
                    await callback(result[5:-1])
                elif pretty_name == "announcement":
                    NotImplemented
