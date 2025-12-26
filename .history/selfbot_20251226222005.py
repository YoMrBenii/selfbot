import sys
from types import ModuleType


if 'audioop' not in sys.modules:
    dummy_audioop = ModuleType('audioop')
    dummy_audioop.tostereo = lambda *args: None 
    sys.modules['audioop'] = dummy_audioop

import discord
import asyncio
from discord.ext import tasks
import time
import os
import string
import random

TOKEN = os.getenv("a")
client = discord.Client()

cooldown_until = 0
your_id = 1118218807694065684


status_messages = [
    "I love you",
    "I love animals",
    "I love food",
    "I love women",
    "I love men"
]
status_index = 0

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    msg_loop.start()
    status_loop.start()
    if not bump.is_running():
        bump.start()
    if bump.is_running():
        print("its running")

@client.event
async def on_message(message):
    global cooldown_until

    if message.author.bot:
        return

    now = time.time()

    if message.author.id == your_id:
        cooldown_until = now + 300

    if message.content.startswith('$treps'):
        await message.channel.send('t!rep <@1118218807694065684>')

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@tasks.loop(seconds=30)
async def msg_loop():
    channel = client.get_channel(1198228961000423486)

    while True:
        try:
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await channel.send(random_string)
            break
        except discord.errors.DiscordServerError as e:
            print(f"[msg_loop] DiscordServerError: {e} — Retrying in 5s...")
            await asyncio.sleep(5)
        except discord.HTTPException as e:
            print(f"[msg_loop] HTTPException: {e} — Retrying in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[msg_loop] Unexpected error: {e} — Retrying in 5s...")
            await asyncio.sleep(5)

@tasks.loop(seconds=30)
async def status_loop():
    global status_index
    custom_status = discord.CustomActivity(name=status_messages[status_index % len(status_messages)])
    await client.change_presence(activity=custom_status)
    status_index += 1

@tasks.loop(seconds=60)
async def bump():
    print("--- Diagnostic Start ---")
    channel = client.get_channel(1108669775099461633)
    if not channel:
        try:
            channel = await client.fetch_channel(1108669775099461633)
        except Exception as e:
            print(f"Failed to fetch channel: {e}")
            return

    # 1. Check permissions for YOUR account in this channel
    perms = channel.permissions_for(channel.guild.me)
    
    print(f"Analyzing permissions in #{channel.name}:")
    print(f"- Use Application Commands: {'✅' if perms.use_application_commands else '❌ (THIS IS THE PROBLEM)'}")
    print(f"- View Channel: {'✅' if perms.view_channel else '❌'}")
    print(f"- Send Messages: {'✅' if perms.send_messages else '❌'}")
    print(f"- Embed Links: {'✅' if perms.embed_links else '❌ (Some bots hide commands if you cant embed)'}")

    # 2. Try to list ALL commands without any filtering
    try:
        count = 0
        async for cmd in channel.slash_commands():
            count += 1
            if count == 1:
                print("Commands are visible! Listing first few:")
            if count <= 5:
                print(f"  > Found: {cmd.name} (Bot ID: {cmd.application_id})")
        
        if count == 0:
            print("Zero commands found. Discord is actively hiding the bot tree from this session.")
        else:
            print(f"Total commands visible to you: {count}")

    except Exception as e:
        print(f"Error while searching: {e}")
    
    print("--- Diagnostic End ---")

client.run(TOKEN)
