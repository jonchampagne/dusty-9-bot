#!/usr/bin/env python3

import os
import os.path
from os.path import dirname, basename, isfile
import glob
import discord
from discord.ext import commands
import json
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

mods = []

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

# Works similar to the loading of all the modules.
# Loop through each mod and execute each one's help()
# which should give back a string.
@bot.command(pass_context=True)
async def help(ctx):

    s = "```\n"
    for mod in mods:
        help_text = getattr(mod, 'help')
        s += help_text(ctx)
        s += "\n"
    s += "```"

    await bot.say(s)

# Import all dynamic modules
# From https://stackoverflow.com/a/1057534
module_files = glob.glob(dirname(__file__) + "/modules/*.py")
modules = [ basename(f)[:-3] for f in module_files if isfile(f) and not f.endswith('__init__.py')]

for modname in modules:
    mod = importlib.import_module("modules." + modname)
    try:
        init = getattr(mod, 'init')
    except AttributeError:
        print("Error loading module: " + modname)
        print("Error: init not found")
    else:
        try:
            help = getattr(mod, 'help')
        except AttributeError:
            print("Error loading module: " + modname)
            print("Error: help not found")
        else:
            if init(bot):
                print("Imported module: " + modname)
                mods.append(mod)
            else:
                print("Error loading module: " + modname)
                print("Error: Failed to initialize")
print()

bot.run(token)
