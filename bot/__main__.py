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
import importlib

# Files used by the bot
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
        await bot.say(traceback.format_exception)

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
