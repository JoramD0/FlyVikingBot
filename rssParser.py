import feedparser, time, os, logging

async def read_feed(rss_url, pretty_name, callback):
# Read last modified and pull feed
    if os.path.exists(f"{pretty_name}_rss_trackfile"):
        with open(f"{pretty_name}_rss_trackfile", "r") as trackfile:
            original_trackfile_time = trackfile.read()
            feed = feedparser.parse(rss_url, modified=original_trackfile_time)
    else:
        original_trackfile_time = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.gmtime()) # To prevent error on first run
        feed = feedparser.parse(rss_url)

    # Write latest modified if new feed
    if feed.status == 200:
        last_check = time.strptime(original_trackfile_time, "%a, %d %b %Y %H:%M:%S %z")

        for entry in reversed(feed.entries):
            try:
                # Check if entry was posted since last check
                if time.mktime(entry.published_parsed) > time.mktime(last_check):
                    if pretty_name == "gallery":
                        await callback(entry.enclosures[0].url)
                    elif pretty_name == "announcement":
                        return_list = [entry.title, entry.link, entry.enclosures[0].url]
                        await callback(return_list)
                    elif pretty_name == "aivlasoft":
                        return_list = [entry.title, entry.link]
                        await callback(return_list)
                    elif pretty_name == "downloads":
                        return_list = [entry.link]
                        await callback(return_list)
                    elif pretty_name == "downloads_update":
                        return_list = [entry.link]
                        await callback(return_list)
            except:
                logging.error(f"rssParser: Error reading entry: {entry}")

            else:
                # Write new time last so in case of error it still posts next time.
                with open(f"{pretty_name}_rss_trackfile", "w") as trackfile:
                    trackfile.write(entry.published)
