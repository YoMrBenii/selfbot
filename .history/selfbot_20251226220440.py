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
    print("Loop heartbeat: Checking for channel...")
    
    # 1. Try cache first
    channel = client.get_channel(1108669775099461633)
    
    # 2. If not in cache, FORCE fetch from API
    if not channel:
        print("Channel not in cache. Fetching from API...")
        try:
            channel = await client.fetch_channel(1108669775099461633)
            print(f"Successfully fetched channel: {channel.name}")
        except Exception as e:
            print(f"Critical Error: Could not fetch channel {e}")
            return # Only exit if even the API can't find it

    try:
        print(f"Searching for slash commands in {channel.name}...")
        command = None
        
        # 3. Iterate the async generator
        async for cmd in channel.slash_commands(query="messages"):
            print(f"Checking command: {cmd.name} from ID: {cmd.application_id}")
            if cmd.application_id == 720351927581278219 and cmd.name == "messages":
                print("Match found! Saving command object.")
                command = cmd
                break
        
        if command:
            print("Step 3: Invoking /messages...")
            await command()
            print("Interaction sent successfully!")
        else:
            print("Search complete: No matching /messages command found.")

    except Exception as e:
        print(f"Error during slash search/invoke: {e}")
client.run(TOKEN)
