import feedparser, re, time

def read_feed(rss_url, pretty_name, callback):
# Read last modified and pull feed
    try:
        with open(f"{pretty_name}_rss_trackfile", "r") as trackfile:
            original_trackfile_time = trackfile.read()
            feed = feedparser.parse(rss_url, modified=original_trackfile_time)
    except:
        feed = feedparser.parse(rss_url)

    # Write latest modified if new feed
    if feed.status == 200:
        with open(f"{pretty_name}_rss_trackfile", "w") as trackfile:
            try:
                trackfile.write(feed.modified)
            except:
                print("Could not write to file")

        for entry in feed.entries:
            last_check = time.strptime(original_trackfile_time, "%a, %d %b %Y %H:%M:%S %Z")

            # Check if entry was posted since last check
            if time.mktime(entry.published_parsed) > time.mktime(last_check):
                result = re.search('src="([^"]+)"', entry.summary).group()
                print(result[5:-1]) # This is the link to the image (get this posted on Discord somehow)
                if pretty_name == "gallery":
                    callback(result[5:-1])
                elif pretty_name == "announcement":
                    NotImplemented

#TODO: Post to Discord (including to discord type)
