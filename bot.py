from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os

# Enable message content intent for commands to work
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # needed for role assignment and reaction roles

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

# Admin check decorator
def is_admin():
    def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# Command: setup_roles - sends a reaction role message for Worker/Customer roles
@bot.command()
@is_admin()
async def setup_roles(ctx):
    embed = discord.Embed(
        title="Choose your role",
        description="React to get your role:\n"
                    "🛠️ for Worker\n"
                    "👤 for Customer"
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("🛠️")
    await message.add_reaction("👤")

    # Save message ID somewhere if needed for persistent reaction role handling

# Reaction role handling
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    # Customize with your role IDs or role names
    worker_role = discord.utils.get(guild.roles, name="Worker")
    customer_role = discord.utils.get(guild.roles, name="Customer")

    if payload.emoji.name == "🛠️" and worker_role:
        await payload.member.add_roles(worker_role)
    elif payload.emoji.name == "👤" and customer_role:
        await payload.member.add_roles(customer_role)

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    worker_role = discord.utils.get(guild.roles, name="Worker")
    customer_role = discord.utils.get(guild.roles, name="Customer")

    if payload.emoji.name == "🛠️" and worker_role:
        await member.remove_roles(worker_role)
    elif payload.emoji.name == "👤" and customer_role:
        await member.remove_roles(customer_role)

# Command: order - sends a message with a Place Order button (admin only)
@bot.command()
@is_admin()
async def order(ctx):
    embed = discord.Embed(title="Place an Order", description="Click the button below to place a new order!")
    button = discord.ui.Button(label="Place Order", style=discord.ButtonStyle.green)

    async def button_callback(interaction):
        # You can customize ticket creation or order handling here
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        order_channel = await guild.create_text_channel(f"order-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"Order channel created: {order_channel.mention}", ephemeral=True)

    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# Command: complete - marks current ticket/order channel complete and closes it (admin only)
@bot.command()
@is_admin()
async def complete(ctx):
    await ctx.send("Marking ticket as complete and closing the channel...")
    await ctx.channel.delete()

# Existing admin commands from before

# Admin command to close a ticket (alias to complete)
@bot.command()
@is_admin()
async def ticket_close(ctx):
    await ctx.send("Closing this ticket...")
    await ctx.channel.delete()

# Admin command to add a role to a user
@bot.command()
@is_admin()
async def role_add(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"Added role {role.name} to {member.mention}")

# Admin command to remove a role from a user
@bot.command()
@is_admin()
async def role_remove(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"Removed role {role.name} from {member.mention}")

# Admin command to send ticket creation panel
@bot.command()
@is_admin()
async def ticket_panel(ctx):
    embed = discord.Embed(title="Support Tickets", description="Click the button below to create a ticket!")
    button = discord.ui.Button(label="Create Ticket", style=discord.ButtonStyle.primary)

    async def button_callback(interaction):
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# Run bot using token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise Exception("❌ DISCORD_BOT_TOKEN not found in environment variables!")

bot.run(TOKEN)
