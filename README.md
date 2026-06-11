# Discord Server Status Bot

A Python Discord bot for managing and monitoring a Discord server. It provides rotating server status, member count voice channels, welcome images, auto role assignment, moderation commands, anti-spam protection, anti-raid locking, and staff logging.

## Features

- Rotating bot presence with server name, total members, and online members.
- Auto-updated voice channels for total member count and online member count.
- Custom welcome image with member avatar.
- Auto role for new members.
- Join and leave logging.
- Anti-spam message protection.
- Anti-raid detection with optional channel lockdown.
- Slash commands for help, ping, purge, say, announce, and unlock all channels.
- Styled Discord embeds.

## Requirements

- Python 3.10 or newer
- A Discord bot token
- A Discord server where you have administrator access
- Discord Developer Portal access

Install Python packages:

```bash
pip install discord.py pillow aiohttp
```

## Files

```text
Discord-Server-Status-Bot/
├── staff_bot.py
├── background.png
├── Montserrat-Bold.ttf
├── Montserrat-Regular.ttf
├── LICENSE
└── README.md
```

## Fields You Must Change

Before running the bot, open `staff_bot.py` and update these values.

### Bot Token

```python
TOKEN = "YOUR_BOT_TOKEN"
```

Use your Discord bot token from the Discord Developer Portal.

Important: never commit your real token to GitHub. If a token was already pushed, reset it in the Discord Developer Portal.

### Server ID

```python
GUILD_ID = 1476203187114479649
```

Replace this with your Discord server ID.

### Server Name

```python
SERVER_NAME = "Lag NPC's"
```

Change this to your server/community name.

### Auto Role

```python
AUTO_ROLE_ID = 1476203187114479655
```

Replace this with the role ID that new members should receive automatically.

### Welcome Channel

```python
WELCOME_CHANNEL_ID = 1483749326789546045
```

Replace this with the channel ID where welcome messages should be sent.

### Logging Channel

```python
MOD_LOG_CHANNEL_ID = 1483101829335089202
```

Replace this with the channel ID where join, leave, raid, and moderation logs should be sent.

### Member Count Voice Channels

```python
ALL_MEMBERS_CHANNEL_ID = 1476219170776416389
ONLINE_MEMBERS_CHANNEL_ID = 1476219174417203282
```

Replace these with voice channel IDs. The bot renames them to show:

```text
Members: <count>
Online: <count>
```

### Anti-Raid Settings

```python
RAID_JOIN_THRESHOLD = 5
RAID_TIME_WINDOW = 10
```

These values mean the bot detects a raid if 5 users join within 10 seconds.

### Anti-Spam Settings

```python
SPAM_WINDOW_SECONDS = 5
SPAM_MAX_MESSAGES = 5
```

These values mean users can send up to 5 messages in 5 seconds before the bot warns them.

### Font Paths

The current code uses absolute Linux paths:

```python
font_big = ImageFont.truetype("/root/bots/lag/Montserrat-Bold.ttf", 90)
font_small = ImageFont.truetype("/root/bots/lag/Montserrat-Regular.ttf", 65)
```

Change them to match your project folder, for example:

```python
font_big = ImageFont.truetype("Montserrat-Bold.ttf", 90)
font_small = ImageFont.truetype("Montserrat-Regular.ttf", 65)
```

## Discord Developer Portal Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application.
3. Open the **Bot** tab and create a bot.
4. Copy the bot token and place it in `TOKEN`.
5. Enable these privileged gateway intents:
   - Server Members Intent
   - Message Content Intent
   - Presence Intent
6. Invite the bot to your server with the required permissions.

Recommended permissions:

- Administrator, easiest for setup
- Manage Channels
- Manage Roles
- Manage Messages
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands

## Running The Bot

Start the bot:

```bash
python staff_bot.py
```

When the bot starts, it syncs slash commands to the configured guild.

## Slash Commands

```text
/help       Show command list
/ping       Show bot latency
/purge      Delete messages from a channel
/say        Send a message as the bot
/announce   Send an embedded announcement
/unlockall  Unlock all text channels after a raid lockdown
```

## VPS Deployment

Install dependencies:

```bash
pip install discord.py pillow aiohttp
```

Run with `screen`:

```bash
screen -S status-bot
python staff_bot.py
```

Or run with `systemd`/PM2 if you want automatic restarts.

## Security Notes

- Do not publish your real bot token.
- Rotate the token immediately if it appears on GitHub or in a public chat.
- Keep the bot role below your highest admin roles.
- Be careful with anti-raid lockdown because it can disable sending messages in all text channels.

## License

This project is licensed under the MIT License.
