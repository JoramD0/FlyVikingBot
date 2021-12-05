import discord, fsaInterface, websiteInterface, json, logging, rssParser
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_permission
from discord_slash.model import SlashCommandPermissionType

logging.basicConfig(filename="discordBot.log", encoding="utf-8", level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s")

# Get credentials
with open("credentials.json", "r", encoding="utf-8") as credentialsFile:
    credentials = json.load(credentialsFile)

# Common channel defines
channelSystemMessages = 739160821740994631
channelScreenshots = 631950027476172810
channelBotDevelopment = 850419733273640990

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, sync_commands=True)

guildId = 631900777794764830
adminRole = 631901856997834778

# Bot active
@client.event
async def on_ready():
    logging.info(f"Bot logged in as {client}")
    read_feed_discord.start()

# rssParser loop
@tasks.loop(seconds=60.0)
async def read_feed_discord():
    await rssParser.read_feed("https://flyviking.net/gallery/images.xml/", "gallery", callback=gallery_send)

@client.event
async def gallery_send(image):
    ch = client.get_channel(channelScreenshots)
    await ch.send(image)

# User left message
@client.event
async def on_member_remove(member):
    ch = client.get_channel(channelSystemMessages)
    await ch.send(f"**{member}** left the server.")

# Screenshot channel image check
@client.event
async def on_message(message):
    logging.info(message)
    if message.channel == client.get_channel(channelScreenshots):
        logging.info(f"{message.content}")
        if len(message.attachments) > 0:
            True
        elif message.content.endswith(".jpg") or message.content.endswith(".png"):
            True
        else:
            logging.info(f"Deleting message without image in #screenshots: {message}")
            await message.delete()

# Slash commands
@slash.slash(name="Airline_Statistics", description="Gets various airline statistics from FSAirlines", guild_ids=[guildId])
async def _stats(ctx):
    data = fsaInterface.getAirlineStats()
    if not data:
        logging.error("Could not retreive data from FSAirlines")
        await ctx.send(":x: ERROR: Could not retreive data from FSAirlines", delete_after=5)
    else:
        embed = discord.Embed(
            title = "Airline Statistics",
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
        await ctx.send(embed=embed)

@slash.slash(
    name="Clear",
    description="Clears multiple message",
    guild_ids=[guildId],
    default_permission=False,
    permissions={
        guildId: [
            create_permission(adminRole, SlashCommandPermissionType.ROLE, True),
        ]
    },
    options=[
        create_option(
            name = "amount",
            description = "Amount of messages to clear",
            option_type = 4,
            required = True
        )
    ]
)
async def _clear(ctx, amount):
    if 0 < amount <= 50:
        deleted = await ctx.channel.purge(limit=amount, bulk=True)
        multiple = ""
        if len(deleted) != 1:
            multiple = "s"
        await ctx.send(content=f":white_check_mark: Deleted {len(deleted)} message{multiple}", delete_after=5)
    else:
        await ctx.send(content=f":x: Amount needs to be between 1 and 50", delete_after=5)

@slash.slash(
    name="Paint_Lookup",
    description="Lookup aircraft paint on the website",
    guild_ids=[guildId],
    options=[
        create_option(
            name = "query",
            description = "Search term",
            option_type = 3,
            required = True
        )
    ]
)
async def _stats(ctx, query):
    data = websiteInterface.fileQuery(query)
    if data is False:
        logging.error("Could not retreive data from website")
        await ctx.send(f":x: ERROR: Could not retreive data from website", delete_after=5)
    elif type(data) is int:
        if data > 1:
            logging.info("Too many matches")
            await ctx.send(":x: ERROR: Too many matches", delete_after=5)
        else:
            logging.info("No matches")
            await ctx.send(":x: ERROR: No matches", delete_after=5)
    else:
        embed = discord.Embed(
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
        await ctx.send(embed=embed)

client.run(credentials["discordBotToken"])
