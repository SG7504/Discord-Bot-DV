import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from datetime import datetime
import os

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

TICKET_REQUEST_CHANNEL = "order-requests"
TICKET_LOG_CHANNEL = "order-logs"
TICKET_CATEGORY_NAME = "Tickets"


# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"✅ Dragon's Vault is online as {bot.user}")


# === ROLE SELECTION MESSAGE ===
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


# === TICKET COMMAND ===
@bot.command()
@commands.has_role("Customer")
async def ticket(ctx):
    customer = ctx.author
    guild = ctx.guild
    log_channel = discord.utils.get(guild.text_channels, name=TICKET_REQUEST_CHANNEL)
    archive_channel = discord.utils.get(guild.text_channels, name=TICKET_LOG_CHANNEL)

    if not log_channel or not archive_channel:
        await ctx.send(f"⚠️ Required channels `{TICKET_REQUEST_CHANNEL}` or `{TICKET_LOG_CHANNEL}` not found.")
        return

    embed = discord.Embed(
        title="New Order Request",
        description=f"{customer.mention} has requested to place an order.",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )

    class ApprovalButtons(View):
        def __init__(self, customer):
            super().__init__(timeout=None)
            self.customer = customer

        @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅")
        async def approve(self, interaction: discord.Interaction, button: Button):
            if not discord.utils.get(interaction.user.roles, name="Administrator"):
                await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
                return

            category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
            if not category:
                category = await guild.create_category(TICKET_CATEGORY_NAME)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.customer: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                discord.utils.get(guild.roles, name="Worker"): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                discord.utils.get(guild.roles, name="Administrator"): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = await guild.create_text_channel(
                name=f"ticket-{self.customer.name}",
                overwrites=overwrites,
                category=category
            )

            await channel.send(f"🎫 Welcome {self.customer.mention}! Please describe your request.")

            await interaction.response.send_message(f"✅ Approved. Ticket created: {channel.mention}", ephemeral=True)

            log_embed = discord.Embed(
                title="✅ Ticket Approved",
                description=f"Customer: {self.customer.mention}\nTicket: {channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await archive_channel.send(embed=log_embed)

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
        async def cancel(self, interaction: discord.Interaction, button: Button):
            if not discord.utils.get(interaction.user.roles, name="Administrator"):
                await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
                return

            await self.customer.send("❌ Your order request has been denied by an admin.")
            await interaction.response.send_message("🚫 Request canceled.", ephemeral=True)

            log_embed = discord.Embed(
                title="❌ Ticket Canceled",
                description=f"Customer: {self.customer.mention}\nCanceled by: {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await archive_channel.send(embed=log_embed)

    await log_channel.send(embed=embed, view=ApprovalButtons(customer))
    await ctx.send("📩 Your order has been sent for admin approval.")


@ticket.error
async def ticket_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("🚫 Only **Customers** can create tickets.")


# === COMPLETE TICKET ===
@bot.command()
@commands.has_role("Administrator")
async def complete(ctx):
    archive_channel = discord.utils.get(ctx.guild.text_channels, name=TICKET_LOG_CHANNEL)
    if not archive_channel:
        await ctx.send("⚠️ Could not find `order-logs` channel.")
        return

    log_embed = discord.Embed(
        title="✔️ Ticket Completed",
        description=f"Channel: `{ctx.channel.name}`\nCompleted by: {ctx.author.mention}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    await archive_channel.send(embed=log_embed)

    await ctx.send("✅ Ticket completed. Closing in 10 seconds...")
    await asyncio.sleep(10)
    await ctx.channel.delete()


# === WORKER QUOTES PRICE ===
@bot.command()
@commands.has_role("Worker")
async def quote(ctx, *, price: str):
    await ctx.send(f"💰 Quoted price: **{price}**. Customer, please confirm payment to an admin.")


# === RUN BOT ===
bot.run(os.getenv("TOKEN"))

