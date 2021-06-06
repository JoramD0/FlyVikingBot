import discord, fsaInterface, json, logging
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_permission
from discord_slash.model import SlashCommandPermissionType

logging.basicConfig(filename="discordBot.log", encoding="utf-8", level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s")

# Get credentials
with open("credentials.json", "r", encoding="utf-8") as credentialsFile:
    credentials = json.load(credentialsFile)

# Common channel defines
channelSystemMessages = 739160821740994631

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, sync_commands=True)

guildId = 631900777794764830
adminRole = 631901856997834778

# Bot active
@client.event
async def on_ready():
    logging.info(f"Bot logged in as {client}")

# User left message
@client.event
async def on_member_remove(member):
    ch = client.get_channel(channelSystemMessages)
    await ch.send(f"**{member}** left the server.")

# Slash commands
@slash.slash(name="Airline_Statistics", description="Gets various airline statistics from FSAirlines", guild_ids=[guildId])
async def _stats(ctx):
    data = fsaInterface.getAirlineStats()
    if not data:
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

client.run(credentials["discordBotToken"])
