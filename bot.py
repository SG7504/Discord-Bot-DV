# bot.py

# === Keeps the bot online on Render ===
from keep_alive import keep_alive
keep_alive()

# === Your Discord Bot ===
import discord
from discord.ext import commands
import os

# Create the bot with command prefix (e.g. !help)
intents = discord.Intents.default()
intents.message_content = True  # Required for newer discord.py versions

bot = commands.Bot(command_prefix="!", intents=intents)

# === Example event ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# === Example command ===
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# === Add your other commands and logic below ===
# ...

# === Run the bot ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Use environment variable for security
if not TOKEN:
    raise Exception("DISCORD_BOT_TOKEN is not set in the environment!")

bot.run(TOKEN)
