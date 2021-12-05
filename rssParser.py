import feedparser, re, time, discordBot

RSS_URL = "https://flyviking.net/gallery/images.xml/"
PRETTY_NAME = "gallery" # Used for discord type (gallery or announcement)

def read_feed(rss_url, pretty_name):
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
                    discordBot.gallery_send(result[5:-1])
                elif pretty_name == "announcement":
                    NotImplemented

def start_loop():
    starttime = time.time()
    while True:
        print("tick")
        read_feed(RSS_URL, PRETTY_NAME)
        time.sleep(60.0 - ((time.time()) - starttime) % 60.0)

#TODO: Make this work for more than 1 RSS feed
#TODO: Execute every x (60?) seconds
#TODO: Post to Discord (including to discord type)
