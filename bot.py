from keep_alive import keep_alive
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import asyncio
from datetime import datetime
import os
import traceback

# Load environment variables
TOKEN = os.getenv("TOKEN")
TICKET_REQUEST_CHANNEL_ID = int(os.getenv("TICKET_REQUEST_CHANNEL_ID"))
TICKET_LOG_CHANNEL_ID = int(os.getenv("TICKET_LOG_CHANNEL_ID"))
ORDER_INFO_CHANNEL_ID = int(os.getenv("ORDER_INFO_CHANNEL_ID"))
PLACE_ORDER_CHANNEL_ID = int(os.getenv("PLACE_ORDER_CHANNEL_ID"))
SELF_ROLE_CHANNEL_ID = int(os.getenv("SELF_ROLE_CHANNEL_ID"))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))

# Intents and bot setup
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

@bot.event
async def on_ready():
    print(f"✅ Dragon's Vault is online as {bot.user}")

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

                async def on_cancel(self, modal_interaction: discord.Interaction):
                    await modal_interaction.response.send_message("❌ Order canceled.", ephemeral=True)

            await interaction.response.send_modal(OrderModal())

    await ctx.send(embed=embed, view=OrderInterface())

async def ticket(interaction, order_text):
    try:
        customer = interaction.user
        guild = interaction.guild
        log_channel = bot.get_channel(TICKET_REQUEST_CHANNEL_ID)
        archive_channel = bot.get_channel(TICKET_LOG_CHANNEL_ID)
        info_channel = bot.get_channel(ORDER_INFO_CHANNEL_ID)

        if not log_channel or not archive_channel or not info_channel:
            await interaction.followup.send("⚠️ Required channels are missing.", ephemeral=True)
            return

        embed = discord.Embed(
            title="New Order Request",
            description=f"{customer.mention} submitted an order:\n\n```{order_text}```",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )

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

                category = bot.get_channel(TICKET_CATEGORY_ID)
                if not category:
                    category = await guild.create_category("Tickets")

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    discord.utils.get(guild.roles, name="Worker"): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    discord.utils.get(guild.roles, name="Administrator"): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.owner: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }

                channel_name = f"ticket-{self.order_text[:30].strip().replace(' ', '-')[:25].lower()}"
                channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    category=category
                )

                status_embed = discord.Embed(
                    title="🟠 Order In Progress",
                    description=f"**Order:** `{self.order_text}`\n**Customer:** {self.customer.mention}\n**Status:** In Progress",
                    color=discord.Color.orange()
                )
                await info_channel.send(embed=status_embed)

                class TicketControls(View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @discord.ui.button(label="Cancel Ticket", style=discord.ButtonStyle.danger, emoji="🗑️")
                    async def cancel_ticket(self, interaction: discord.Interaction, button: Button):
                        is_admin = discord.utils.get(interaction.user.roles, name="Administrator")
                        is_owner = interaction.user.id == guild.owner_id
                        if not is_admin and not is_owner:
                            await interaction.response.send_message("❌ Only admins or the owner can cancel.", ephemeral=True)
                            return

                        await interaction.channel.send("❌ Ticket canceled. Closing in 5 seconds...")
                        await asyncio.sleep(5)
                        await interaction.channel.delete()

                        cancel_embed = discord.Embed(
                            title="🗑️ Ticket Canceled",
                            description=f"Canceled by: {interaction.user.mention}\nOrder: `{self.order_text}`",
                            color=discord.Color.red(),
                            timestamp=datetime.utcnow()
                        )
                        await archive_channel.send(embed=cancel_embed)

                await channel.send(
                    f"🎫 **Order Details:**\n```{self.order_text}```\n"
                    "To claim this order simple type 'order claimed' and amount which you can handle",
                    view=TicketControls()
                )
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

        await log_channel.send(embed=embed, view=ApprovalButtons(customer, order_text))

    except Exception:
        print(f"❌ Error in ticket():\n{traceback.format_exc()}")
        try:
            await interaction.followup.send("⚠️ An unexpected error occurred. Please contact an admin.", ephemeral=True)
        except:
            pass

@bot.command()
@commands.has_role("Administrator")
async def complete(ctx):
    archive_channel = bot.get_channel(TICKET_LOG_CHANNEL_ID)
    if not archive_channel:
        await ctx.send("⚠️ Could not find order-logs channel.")
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

@bot.command()
@commands.has_role("Worker")
async def quote(ctx, *, price: str):
    await ctx.send(f"💰 Quoted price: **{price}**. Customer, please confirm payment to an admin.")

keep_alive()
bot.run(TOKEN)
