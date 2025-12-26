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
    print("--- Attempting Force Sync Bump ---")
    channel = client.get_channel(1108669775099461633)
    if not channel:
        try:
            channel = await client.fetch_channel(1108669775099461633)
        except:
            return

    try:
        # 1. THE FIX: Force Discord to send the command tree for this specific server
        # This mimics clicking the "/" button in the UI.
        # We target the guild (server) specifically.
        guild = channel.guild
        print(f"Force-syncing commands for server: {guild.name}...")
        
        # This populates the internal cache with the commands
        # Note: In some versions, this might be named slightly differently or require awaiting
        # If this line errors, I have a backup method below.
        commands_payload = await channel.application_commands() 
        
        # 2. Now we iterate through the payload we just fetched directly
        target_command = None
        for cmd in commands_payload:
            # print(f"Seen: {cmd.name} ({cmd.application_id})") # Uncomment to debug
            if cmd.application_id == 720351927581278219 and cmd.name == "messages":
                target_command = cmd
                break
        
        if target_command:
            print(f"Command found! Triggering {target_command.name}...")
            await target_command()
            print("Interaction dispatched.")
        else:
            print("Force sync complete, but command still not found in the payload.")

    except AttributeError:
        # If 'application_commands' doesn't exist, we try the search fallback
        print("AttributeError: switching to search fallback...")
        async for cmd in channel.slash_commands(query="messages"):
            if cmd.application_id == 720351927581278219:
                await cmd()
                print("Fallback execution sent.")
                return

    except Exception as e:
        print(f"Error: {e}")

client.run(TOKEN)
