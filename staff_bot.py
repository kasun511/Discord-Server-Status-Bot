#-*- coding: utf-8 -*-

# ==========================
# IMPORTS
# ==========================

import time
import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands

# ==========================
# CONFIG
# ==========================

TOKEN = "MTQ4MzExMTYzMDczMTQ3NzAxMg.GBdlQs.yDeDfDlIsAEIm29XsPbwvTLv1dV5ZW_0x6ye60"
GUILD_ID = 1476203187114479649

SERVER_NAME = "Lag NPC's"

# auto role and antiraid
AUTO_ROLE_ID = 1476203187114479655  # your role id
RAID_JOIN_THRESHOLD = 5   # joins
RAID_TIME_WINDOW = 10     # seconds

# welcomer
WELCOME_CHANNEL_ID = 1483749326789546045

# Logging
MOD_LOG_CHANNEL_ID = 1483101829335089202
ALL_MEMBERS_CHANNEL_ID = 1476219170776416389
ONLINE_MEMBERS_CHANNEL_ID = 1476219174417203282

# Anti Spam
SPAM_WINDOW_SECONDS = 5
SPAM_MAX_MESSAGES = 5

# ==========================
# THEME
# ==========================

class Theme:
    PRIMARY = 0x5865F2
    SUCCESS = 0x2ECC71
    WARNING = 0xF39C12
    ERROR = 0xE74C3C
    INFO = 0x3498DB
    PREMIUM = 0x9B59B6
    DARK = 0x2C2F33

# ==========================
# BOT SETUP
# ==========================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_message_times = {}

# ==========================
# UTILITIES
# ==========================

def get_main_guild():
    return bot.get_guild(GUILD_ID)

def get_mod_log_channel():
    guild = get_main_guild()
    if guild:
        return guild.get_channel(MOD_LOG_CHANNEL_ID)

def create_embed(title=None, description=None, color=Theme.PRIMARY):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.timestamp = discord.utils.utcnow()
    return embed

async def log_action(title, description, color=Theme.DARK):

    channel = get_mod_log_channel()

    if not channel:
        return
    
    embed = create_embed(title, description, color)
    embed.set_footer(text=SERVER_NAME)

    try:
        await channel.send(embed=embed)
    except:
        pass

# ==========================
# MEMBER COUNT CHANNELS
# ==========================

async def update_member_counts():

    guild = get_main_guild()
    if not guild:
        return

    total = guild.member_count
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)

    all_ch = guild.get_channel(ALL_MEMBERS_CHANNEL_ID)
    on_ch = guild.get_channel(ONLINE_MEMBERS_CHANNEL_ID)

    try:
        if isinstance(all_ch, discord.VoiceChannel):

            name = f"Members: {total}"

            if all_ch.name != name:
                await all_ch.edit(name=name)

        if isinstance(on_ch, discord.VoiceChannel):

            name = f"Online: {online}"

            if on_ch.name != name:
                await on_ch.edit(name=name)

    except:
        pass

@tasks.loop(minutes=5)
async def stats_loop():
    await update_member_counts()

@stats_loop.before_loop
async def before_stats_loop():
    await bot.wait_until_ready()

# ==========================
# ROTATING STATUS
# ==========================

@tasks.loop(seconds=30)
async def rotating_status():

    guild = bot.get_guild(GUILD_ID)

    if not guild:
        return

    total_members = guild.member_count
    online_members = sum(
        1 for m in guild.members if m.status != discord.Status.offline
    )

    statuses = [
        SERVER_NAME,
        f"{total_members} Members",
        f"{online_members} Online"
    ]

    for status in statuses:

        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=status
            )
        )

        await asyncio.sleep(10)

# ==========================
# welcomer
# ==========================

from PIL import Image, ImageDraw, ImageFont, ImageOps
import aiohttp
import io

async def generate_welcome_image(member):

    width, height = 1000, 400

    # Background
    image = Image.open("background.png").resize((width, height)).convert("RGBA")

    # Dark overlay
    # overlay = Image.new("RGBA", (width, height), (0, 0, 0, 140))
    # image.paste(overlay, (0, 0), overlay)

    draw = ImageDraw.Draw(image)

    # Avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(member.display_avatar.url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((230, 230))

    mask = Image.new("L", (230, 230), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 230, 230), fill=255)
    avatar.putalpha(mask)

    image.paste(avatar, (60, 85), avatar)

    # Fonts (BIG)
    font_big = ImageFont.truetype("/root/bots/lag/Montserrat-Bold.ttf", 90)
    font_small = ImageFont.truetype("/root/bots/lag/Montserrat-Regular.ttf", 65)

    # Text
    draw.text((340, 110), "WELCOME", font=font_big, fill=(0, 0, 0))
    draw.text((340, 220), member.name, font=font_small, fill=(0, 0, 0))

    # Save
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)

    return buffer

# ==========================
# EVENTS
# ==========================

@bot.event
async def on_ready():

    print(f"\n{'═'*40}")
    print(f"  {bot.user.name}")
    print(f"  Servers: {len(bot.guilds)}")
    print(f"{'═'*40}\n")

    try:

        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)

        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

    if not stats_loop.is_running():
        stats_loop.start()

    if not rotating_status.is_running():
        rotating_status.start()

@bot.event
async def on_member_remove(member):

    if member.bot:
        return

    await log_action(
        "Member Left",
        f"{member} (`{member.id}`)",
        Theme.WARNING
    )

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    now = time.time()
    uid = message.author.id

    if uid not in user_message_times:
        user_message_times[uid] = []

    user_message_times[uid].append(now)

    user_message_times[uid] = [
        t for t in user_message_times[uid]
        if now - t <= SPAM_WINDOW_SECONDS
    ]

    if len(user_message_times[uid]) > SPAM_MAX_MESSAGES:

        try:
            await message.delete()
        except:
            pass

        try:

            embed = create_embed(
                "Slow Down",
                f"{message.author.mention}, you're sending messages too fast.",
                Theme.WARNING
            )

            await message.channel.send(
                embed=embed,
                delete_after=5
            )

        except:
            pass

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):

    if member.bot:
        return

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        image = await generate_welcome_image(member)
        file = discord.File(image, filename="welcome.png")

        await channel.send(
            content=f"Welcome {member.mention}",
            file=file
        )


@bot.event
async def on_member_join(member):

    if member.bot:
        return

    # ==========================
    # AUTO ROLE
    # ==========================
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    # ==========================
    # GENERATE IMAGE
    # ==========================
    image = await generate_welcome_image(member)

    # ==========================
    # SEND WELCOME
    # ==========================
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        file = discord.File(image, filename="welcome.png")

        await channel.send(
            content=f"Welcome to the community \U0001F44B {member.mention}",
            file=file
        )

    # ==========================
    # LOG JOIN
    # ==========================
    await log_action(
        "Member Joined",
        f"{member} (`{member.id}`)",
        Theme.SUCCESS
    )
    # ==========================
    # AUTO ROLE
    # ==========================

    role = member.guild.get_role(AUTO_ROLE_ID)

    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    # ==========================
    # LOG JOIN
    # ==========================

    await log_action(
        "Member Joined",
        f"{member.mention} (`{member.id}`)",
        Theme.SUCCESS
    )

    # ==========================
    # ANTI RAID TRACKING
    # ==========================

    now = time.time()

    if not hasattr(bot, "join_times"):
        bot.join_times = []

    bot.join_times.append(now)

    # keep only recent joins
    bot.join_times = [
        t for t in bot.join_times
        if now - t <= RAID_TIME_WINDOW
    ]

    # ==========================
    # RAID DETECTED
    # ==========================

    if len(bot.join_times) >= RAID_JOIN_THRESHOLD:

        await log_action(
            "RAID DETECTED",
            f"{len(bot.join_times)} users joined in {RAID_TIME_WINDOW}s",
            Theme.ERROR
        )

        # Optional: lock all channels
        for channel in member.guild.text_channels:
            try:
                overwrite = channel.overwrites_for(member.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(member.guild.default_role, overwrite=overwrite)
            except:
                continue
                
# ==========================
# COMMANDS
# ==========================

@bot.tree.command(name="help", description="View all commands")
async def help_cmd(interaction: discord.Interaction):

    embed = create_embed(
        "Command List",
        "All available commands"
    )

    embed.add_field(
        name="Moderation",
        value="`purge` `slowmode` `lock` `unlock`",
        inline=False
    )

    embed.add_field(
        name="Utility",
        value="`help` `ping`",
        inline=False
    )

    embed.add_field(
        name="Staff",
        value="`say` `announce`",
        inline=False
    )

    embed.set_footer(text=SERVER_NAME)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="unlockall", description="Unlock all channels")
async def unlockall(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            embed=create_embed("Error", "Admin only", Theme.ERROR),
            ephemeral=True
        )

    guild = interaction.guild

    for channel in guild.text_channels:
        try:
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = True
            await channel.set_permissions(guild.default_role, overwrite=overwrite)
        except:
            continue

    await interaction.response.send_message(
        embed=create_embed("Unlocked", "All channels unlocked", Theme.SUCCESS)
    )
    
# ==========================
# PING
# ==========================

@bot.tree.command(name="ping", description="Check latency")
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    embed = create_embed(
        "Latency",
        f"`{latency}ms`",
        Theme.SUCCESS
    )

    await interaction.response.send_message(embed=embed)

# ==========================
# PURGE
# ==========================

@bot.tree.command(name="purge", description="Delete messages")
@app_commands.describe(amount="Amount (1-100)")
async def purge(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:

        return await interaction.response.send_message(
            embed=create_embed("Error", "Missing permission", Theme.ERROR),
            ephemeral=True
        )

    amount = max(1, min(100, amount))

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        embed=create_embed(
            "Purge Complete",
            f"Deleted {len(deleted)} messages",
            Theme.SUCCESS
        ),
        ephemeral=True
    )

# ==========================
# SAY
# ==========================

@bot.tree.command(name="say", description="Send message as bot")
@app_commands.describe(message="Message content")
async def say(interaction: discord.Interaction, message: str):

    if not interaction.user.guild_permissions.administrator:

        return await interaction.response.send_message(
            embed=create_embed("Error", "Admin only", Theme.ERROR),
            ephemeral=True
        )

    await interaction.response.send_message(
        embed=create_embed("Sent", "Message sent", Theme.SUCCESS),
        ephemeral=True
    )

    await interaction.channel.send(message)

# ==========================
# ANNOUNCE
# ==========================

@bot.tree.command(name="announce", description="Send announcement")
@app_commands.describe(title="Title", message="Message")
async def announce(interaction: discord.Interaction, title: str, message: str):

    if not interaction.user.guild_permissions.administrator:

        return await interaction.response.send_message(
            embed=create_embed("Error", "Admin only", Theme.ERROR),
            ephemeral=True
        )

    embed = create_embed(title, message, Theme.PREMIUM)
    embed.set_footer(text=SERVER_NAME)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        embed=create_embed("Announcement Sent", "", Theme.SUCCESS),
        ephemeral=True
    )

# ==========================
# RUN BOT
# ==========================

bot.run(TOKEN)
