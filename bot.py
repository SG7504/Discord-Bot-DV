# bot.py

from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os

# Enable message content intent for commands to work
intents = discord.Intents.default()
intents.message_content = True

# Set command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run bot using token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise Exception("❌ DISCORD_BOT_TOKEN not found in environment variables!")

bot.run(TOKEN)
