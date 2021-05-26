import os
import os.path
from os.path import dirname, basename, isfile
import glob
import discord
from discord.ext import commands
import json
import importlib
import traceback
import config

# Load the token from the text file
f = open('token.txt')
token = f.readline()
f.close()

# Dynamically load modules
# From https://stackoverflow.com/a/1057534
mods = []
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
      try:
        if init(bot):
          print("Imported module: " + modname)
          mods.append(mod)
        else:
          print("Error loading module: " + modname)
          print("Error: Failed to initialize")
      except Exception as e:
        print("Error loading module: " + modname)
        print(traceback.format_exc())

# Set up the basics of the bot
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  for mod in mods:
    ready = getattr(mod, 'on_ready')
    ready()

@bot.command(pass_context = True)
async def help(ctx):
  s = "```\n"
  for mod in mods:
    help_text = getattr(mod, 'help')
    s += help_text(ctx)
    s += "\n"
  s += 'Source code available at https://github.com/jonchampagne/dusty-9-bot'
  s += '```'
  await ctx.send(s)

# Start the actual main bot process
bot.run(token)