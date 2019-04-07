#!/usr/bin/env python3

import os
import os.path
from os.path import dirname, basename, isfile
import glob
import discord
from discord.ext import commands
import asyncio
import random
from textwrap import wrap
import traceback
import datetime
import json
import dice
import datetime
import importlib

# Files used by the bot
LAST_SEEN_FILE = 'last_seen.json'
BOTS_FILE = 'bot_credentials.json'

# Test bot to launch
BOT_NAME = 'Production'

bot = commands.Bot(command_prefix = '!', case_insensitive = True)
server = None
pwd = os.path.dirname(os.path.realpath(__file__))

bot_tokens = json.loads(open(BOTS_FILE).read())
token = bot_tokens[BOT_NAME]

bot.remove_command("help")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')
    for s in bot.servers:
        if s.name == 'Dusty 9':
            server = s
            print('Found server: ' + server.name)
            break

@bot.command()
async def help():
    s = "```\n"
    s += "Commands:\n"
    s += "!flip: Flip a coin\n"
    s += "!flip n: Flip n coins\n"
    s += "!roll X: Rolls d a die or dice, specified in standard die notation (XdY)\n"
    s += "!xkcd n: Pulls up XKCD #n \n"
    s += "!roll_stats X: Various statistics of a roll specified in standard die notation (XdY)\n"
    s += "!last_seen <username>: When was <username> last online?\n"
    s += "!acc: v1,v2,t Calculate acceleration, with V1 (Initial Velocity), V2 (Second Velocity), and time. For velocity, use consistent units\n"
    s += "```"

    await bot.say(s)

@bot.command()
async def flip(count = 1):
    if count == None:
        count = 1

    try:
        outstr = ""

        x = int(count)

        if x > 500:
            await bot.say("Are you out of your mind!?! No way I'm flipping a coin " + str(x) + " times!")
            return

        for i in range(x):
            rnum = random.random()
            if rnum < 0.495:
                outstr += "Heads! "
            elif rnum > 0.505:
                outstr += "Tails! "
            else:
                outstr += "It landed on it's side... "

        splitlength = 1995

        s = wrap(outstr, splitlength)

        for i in s:
            await bot.say(i)

    except Exception as e:
        await bot.say("Error: " + str(e))
        print(traceback.format_exc())


@bot.command()
async def roll(dice : str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))

    try:
        await bot.say(result)
    except Exception:
        await bot.say(sys.exc_info()[0])

@bot.command()
async def roll_stats(dicestr : str):
    maximum = dice.roll_max(dicestr)

    # The roll methods can either return an int or a list of ints, depending on input.
    # If we get a list of ints, just add them up.
    if isinstance(maximum, list):
        x = 0
        for i in maximum:
            x += i
        maximum = x

    minimum = dice.roll_min(dicestr)
    if isinstance(minimum, list):
        x = 0
        for i in minimum:
            x += i
        minimum = x

    typical = (minimum + maximum) / 2
    await bot.say("Minimum: " + str(minimum))
    await bot.say("Maximum: " + str(maximum))
    await bot.say("Typical roll: " + str(typical))

@bot.command(pass_context=True)
async def last_seen(ctx, *args):
    # Spaces deliminate args. Gather them all up into a username.
    username = ""
    for arg in args:
        username += arg + " "
    username = username.strip().lower()

    print(username)

    userid = 0

    # We got an @username. Handy!
    # We still resolve to a username and then resolve back to a
    # userid to make sure the user actually exists on this server.
    # Efficient? No. Works? Yup!
    if username.startswith("<@"):
        # Sometimes the format is <@123456789> and sometimes it's <@!123456789>. Not sure why.
        # Perhaps it has to do with a user being an admin?
        uid = username.strip("<@").strip(">")
        uid = uid.strip("!")
        for member in list(ctx.message.server.members):
            if member.id == uid:
                username = member.name.lower()
                print(username)
                break

    # Get the ID from the user name
    for member in ctx.message.server.members:
        # encode/decode used to remove unicode characters, such as emoji
        member_name = member.name.encode('ascii', 'ignore').decode('ascii').strip()
        if member_name.lower() == username:
            userid = member.id

    # Build our response
    response = ""
    if userid == 0:
        response = "Unknown user " + username
    else:
        try:
            seen = last_seen[userid].strftime('%A, %B %d at %I:%M%p')
        except Exception as e:
            print(e)
            seen = None

        if seen != None:
            response = "Last saw " + username + " on " + seen
        else:
            response = "Never seen " + username
            response += "\nUser ID: "+ userid

    await bot.say(response)

@bot.command()
async def acceleration(v1=None, v2=None, time=None):
    try:

        outstr = ""
        if (v1 == None) or (v2 == None) or (time == None):
            outstr = "You must enter all the values!"
        elif (time == 0):
            outstr = "Time cannot be zero!"
        else:
            v2_int = int(v2);
            v1_int = int(v1);
            time_int = int(time);
            outstr = (v2_int - v1_int)/time_int
        await bot.say(outstr);
    except Exception as e:
        await bot.say("Error: " + str(e))
        await bot.say(traceback.format_exc())

def save_last_seen():
    f = open(LAST_SEEN_FILE, 'w')
    f.write(json.dumps(last_seen, default=str))
    f.close()

def load_last_seen():
    try:
        f = open(LAST_SEEN_FILE, 'r')
    except FileNotFoundError:

        # If the file doesn't exist, create it.
        f2 = open(LAST_SEEN_FILE, 'w')
        f2.write("{}")
        f2.close()
        last_seen = dict()
        return last_seen

    imported = json.loads(f.read())
    f.close()

    last_seen = dict()

    for i in imported:
        datestring = imported[i]
        last_seen[i] = datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S.%f') # http://strftime.org

    return last_seen

async def log_people_seen():
    await bot.wait_until_ready()

    while not bot.is_closed:
        now = datetime.datetime.now()

        for server in bot.servers:
            for member in server.members:
                if str(member.status) != "offline":
                    last_seen[member.id] = now

        save_last_seen()
        await asyncio.sleep(60)




last_seen = load_last_seen()

bot.loop.create_task(log_people_seen())

# Import all dynamic modules
# From https://stackoverflow.com/a/1057534
module_files = glob.glob(dirname(__file__) + "/modules/*.py")
modules = [ basename(f)[:-3] for f in module_files if isfile(f) and not f.endswith('__init__.py')]

for modname in modules:
    mod = importlib.import_module("modules." + modname)
    init = getattr(mod, 'init')
    if init(bot):
        print("Imported module: " + modname)
    else:
        print("Error loading module: " + modname)
print()

bot.run(token)