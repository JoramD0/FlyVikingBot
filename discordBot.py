import fsaInterface, websiteInterface, json, logging, rssParser, asyncio, interactions, sys

logging.basicConfig(
    handlers=[
        logging.FileHandler("discordBot.log"),
        logging.StreamHandler(sys.stdout)
    ],
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)

# Get credentials
with open("credentials.json", "r", encoding="utf-8") as credentialsFile:
    credentials = json.load(credentialsFile)

bot = interactions.Client(token=credentials["discordBotToken"], logger=logging.getLogger())

# Roles
role_everyone = 631900777794764830

# Channels
channel_announcements = 631949277559783457
channel_news = 672891056001384488
channel_screenshots = 631950027476172810
channel_development = 850419733273640990

# Custom emojis
emoji_flyvikingv = "<:FlyVikingV:696048915463798835>"
emoji_aivlasoft_pda = "<:aivlasoft_pda:1110634345410084924>"
emoji_aivlasoft_server = "<:aivlasoft_server:1110634344227278978>"
emoji_arma = "<:arma:696048882202968094>"

async def main():
    await bot.astart()

@interactions.listen(interactions.api.events.Startup)
async def startup_func():
    logging.info(f"Bot logged in as {bot}")
    asyncio.create_task(read_feed_discord())

@interactions.listen()
async def on_error(error: interactions.api.events.Error):
    logging.error(error)

# rssParser loop
async def read_feed_discord():
    while True:
        # ("link", "pretty_name", callback)
        await rssParser.read_feed("https://flyviking.net/rss/1-gallery.xml/", "gallery", callback=gallery_send)
        await rssParser.read_feed("https://flyviking.net/rss/3-announcements.xml/", "announcement", callback=announcement_send)
        #await rssParser.read_feed("https://forum.aivlasoft.com/forum/18-announcements.xml/", "aivlasoft", callback=aivlasoft_send) # No longer available
        await rssParser.read_feed("https://flyviking.net/rss/4-downloads.xml/", "downloads", callback=downloads_send)
        await rssParser.read_feed("https://flyviking.net/rss/5-downloads-update.xml/", "downloads_update", callback=downloads_update_send)
        await asyncio.sleep(60)

@interactions.listen()
async def gallery_send(image):
    channel = await bot.fetch_channel(channel_id=channel_screenshots)
    await channel.send(image)

@interactions.listen()
async def announcement_send(list):
    embed = interactions.Embed(
        title = list[0],
        url = list[1],
        color = 0xed2001
    )
    try:
        embed.set_thumbnail(
            url = list[2]
        )
    except:
        logging.info(f"No image attached to announcement {list[0]}, posting without.")

    channel = await bot.fetch_channel(channel_id=channel_announcements)
    await channel.send("@everyone", embeds=embed, allowed_mentions=interactions.AllowedMentions(roles=[role_everyone]))

@interactions.listen()
async def aivlasoft_send(list):
    channel = await bot.fetch_channel(channel_id=channel_news)
    await channel.send(f"{emoji_aivlasoft_pda} **Aivlasoft:**\n\n[{list[0]}]({list[1]})")

@interactions.listen()
async def downloads_send(link):
    channel = await bot.fetch_channel(channel_id=channel_announcements)
    await channel.send(f"## [New file available!]({link[0]})")

@interactions.listen()
async def downloads_update_send(link):
    channel = await bot.fetch_channel(channel_id=channel_announcements)
    await channel.send(f"## [New file version available!]({link[0]})")

# Slash commands
@interactions.slash_command(
    name="airline_statistics",
    description="Gets various airline statistics from FSAirlines"
)
async def airline_statistics(ctx: interactions.SlashContext):
    data = fsaInterface.getAirlineStats()
    if not data:
        logging.error("Could not retreive data from FSAirlines")
        await ctx.send(":x: ERROR: Could not retreive data from FSAirlines", ephemeral=True, delete_after=10)
    else:
        embed = interactions.Embed(
            title = f"{emoji_flyvikingv} Airline Statistics",
            description = "Various airline-wide statistics",
            color = 0xed2001
        )
        embed.add_field(
            name = "Flights",
            value = f"{int(data['flights']):,}",
            inline = True
        )
        embed.add_field(
            name = "Hours flown",
            value = f"{int(data['hours']):,}",
            inline = True
        )
        embed.add_field(
            name = "Distance Flown",
            value = f"{int(data['distance']):,}nm",
            inline = True
        )
        embed.add_field(
            name = "Fuel Used",
            value = f"{int(data['fuel_used']):,}kg",
            inline = True
        )
        embed.add_field(
            name = "Passengers Moved",
            value = f"{int(data['pax']):,}",
            inline = True
        )
        embed.add_field(
            name = "Generic Cargo Moved",
            value = f"{int(data['cargo_kg']):,}kg",
            inline = True
        )
        embed.add_field(
            name = "Packages Moved",
            value = f"{int(data['packages_kg']):,}kg",
            inline = True
        )
        await ctx.send(embeds=embed)

@interactions.slash_command(
    name="clear",
    description="Clears multiple message",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
@interactions.slash_option(
    name="amount",
    description = "Amount of messages to clear",
    required = True,
    opt_type=interactions.OptionType.INTEGER,
    min_value=1,
    max_value=50
)
async def clear(ctx: interactions.SlashContext, amount: int):
    await ctx.channel.purge(amount, reason=None)
    await ctx.send(f":white_check_mark: Deleted {amount} messages.", ephemeral=True, delete_after=10)

@interactions.slash_command(
    name="paint_lookup",
    description="Lookup aircraft paint on the website"
)
@interactions.slash_option(
    name = "query",
    description = "Search term",
    opt_type = interactions.OptionType.STRING,
    required = True
)
async def paint_lookup(ctx: interactions.SlashContext, query: str):
    data = websiteInterface.fileQuery(query)
    if data is False:
        logging.error("Could not retreive data from website")
        await ctx.send(f":x: ERROR: Could not retreive data from website", ephemeral=True, delete_after=10)
    elif type(data) is int:
        if data > 1:
            logging.info(f"Too many matches")
            await ctx.send(":x: ERROR: Too many matches", ephemeral=True, delete_after=10)
        else:
            logging.info("No matches")
            await ctx.send(":x: ERROR: No matches", ephemeral=True, delete_after=10)
    else:
        embed = interactions.Embed(
            title = data["title"],
            url = data["url"],
            color = 0xed2001
        )
        if data["author"]["photoUrlIsDefault"]:
            embed.set_author(
                name = data["author"]["name"],
                url = data["author"]["profileUrl"]
            )
        else:
            embed.set_author(
                name = data["author"]["name"],
                url = data["author"]["profileUrl"],
                icon_url = data["author"]["photoUrl"]
            )
        if data["primaryScreenshot"] is not None:
            embed.set_image(
                url = data["primaryScreenshot"]["url"]
            )
        await ctx.send(embeds=embed)

asyncio.run(main())
