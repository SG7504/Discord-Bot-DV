# === Load Environment ===
from dotenv import load_dotenv
load_dotenv()

import os
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
from flask import Flask
import threading
import asyncio

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_OPTIONS = {
    "🟦": "Worker",
    "🟩": "Customer"
}

# === CHANNEL & CATEGORY IDs ===
TICKET_CATEGORY_ID = 1376843550481715230
TICKET_REQUEST_CHANNEL_ID = 1370319093487632435
TICKET_LOG_CHANNEL_ID = 1370319422430122024
ORDER_INFO_CHANNEL_ID = 1376818171696381952
PLACE_ORDER_CHANNEL_ID = 1368081952913096815
SELF_ROLE_CHANNEL_ID = 1368958759115821278

# === Flask Web Server ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.start()

# === Bot Events ===
@bot.event
async def on_ready():
    print(f"✅ Dragon's Vault is online as {bot.user}")

# === Role Selection Command ===
@bot.command()
async def setup_roles(ctx):
    embed = discord.Embed(
        title="Choose Your Role",
        description="React to get a role:\n\n🟦 - Worker\n🟩 - Customer",
        color=discord.Color.gold()
    )
    msg = await ctx.send(embed=embed)
    for emoji in ROLE_OPTIONS:
        await msg.add_reaction(emoji)
    bot.role_msg_id = msg.id

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.message_id != getattr(bot, 'role_msg_id', None):
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role_name = ROLE_OPTIONS.get(str(payload.emoji))

    if role_name:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name)
        await member.add_roles(role)
        print(f"✅ Assigned {role.name} to {member.name}")

# === Order Command ===
@bot.command(name="order")
@commands.has_permissions(administrator=True)
async def show_order_button(ctx):
    embed = discord.Embed(
        title="Welcome to Dragon's Vault",
        description="Hello customers! Click the **Place Order** button if you'd like to request a service.",
        color=discord.Color.blue()
    )

    class OrderInterface(View):
        @discord.ui.button(label="Place Order", style=discord.ButtonStyle.primary, emoji="📩")
        async def place_order(self, interaction: discord.Interaction, button: Button):
            class OrderModal(Modal, title="Place Your Order"):
                order_details = TextInput(label="Describe what you need", style=discord.TextStyle.paragraph)

                async def on_submit(self, modal_interaction: discord.Interaction):
                    await modal_interaction.response.send_message("✅ Your order was submitted for approval!", ephemeral=True)
                    await ticket(modal_interaction, self.order_details.value)

            await interaction.response.send_modal(OrderModal())

    await ctx.send(embed=embed, view=OrderInterface())

# === Ticket Workflow ===
async def ticket(interaction, order_text):
    customer = interaction.user
    guild = interaction.guild
    log_channel = guild.get_channel(TICKET_REQUEST_CHANNEL_ID)
    archive_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
    info_channel = guild.get_channel(ORDER_INFO_CHANNEL_ID)
    category = guild.get_channel(TICKET_CATEGORY_ID)

    if not all([log_channel, archive_channel, info_channel]):
        await interaction.followup.send("⚠️ Missing necessary channels.", ephemeral=True)
        return

    embed = discord.Embed(
        title="New Order Request",
        description=f"{customer.mention} submitted an order:\n\n```{order_text}```",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    await log_channel.send(embed=embed)

    class ApprovalButtons(View):
        def __init__(self, customer, order_text):
            super().__init__(timeout=None)
            self.customer = customer
            self.order_text = order_text

        @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅")
        async def approve(self, interaction: discord.Interaction, button: Button):
            if not discord.utils.get(interaction.user.roles, name="Administrator"):
                await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
                return

            nonlocal category
            if category is None:
                category = await guild.create_category("Tickets")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.utils.get(guild.roles, name="Worker"): discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(guild.roles, name="Administrator"): discord.PermissionOverwrite(read_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }

            channel = await guild.create_text_channel(
                name=f"ticket-{self.order_text[:25].replace(' ', '-').lower()}",
                overwrites=overwrites,
                category=category
            )

            status_embed = discord.Embed(
                title="🟠 Order In Progress",
                description=f"**Order:** `{self.order_text}`\n**Customer:** {self.customer.mention}\n**Status:** In Progress",
                color=discord.Color.orange()
            )
            await info_channel.send(embed=status_embed)

            await interaction.response.send_message(f"✅ Approved and created ticket: {channel.mention}", ephemeral=True)

        @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="❌")
        async def reject(self, interaction: discord.Interaction, button: Button):
            await archive_channel.send(
                f"❌ Order rejected from {self.customer.mention}:\n```{self.order_text}```"
            )
            await interaction.response.send_message("Order rejected and logged.", ephemeral=True)

    await log_channel.send(view=ApprovalButtons(customer, order_text))

# === Start Flask + Bot ===
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("TOKEN")
    bot.run(TOKEN)
