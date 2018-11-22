#!/bin/env python3

import os
import discord
from discord.ext import commands
import asyncio
from credentials import token
import random
from textwrap import wrap
import traceback
import datetime
import xkcd as libxkcd
import json
import dice
import datetime

WATCH_XKCD_CONF_FILE = 'watch_xkcd_conf.json'
LAST_SEEN_FILE = 'last_seen.json'

bot = commands.Bot(command_prefix = '!', case_insensitive = True)
server = None
pwd = os.path.dirname(os.path.realpath(__file__))

xkcd_conf = json.loads(open(WATCH_XKCD_CONF_FILE).read())
watch_list = xkcd_conf['channels']

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
    s += "!last_seen <username>: When was <username> last online?"
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
async def xkcd(ctx, num: str):
    await show_xkcd(num, ctx.message.channel)

@bot.command(pass_context=True)
async def watch_xkcd(ctx):
    id = ctx.message.channel.id
    if id in watch_list:
        watch_list.remove(id)
        message = "Removed channel #" + ctx.message.channel.name + " from XKCD watch list"
    else:
        watch_list.append(id)
        message = "Added channel #" + ctx.message.channel.name + " to XKCD watch list"

    save_xkcd_conf()
    await bot.say(message)

@bot.command(pass_context=True)
async def last_seen(ctx, *args):
    # Spaces deliminate args. Gather them all up into a username.
    username = ""
    for arg in args:
        username += arg + " "
    username = username.strip()

    userid = 0

    # We got an @username. Handy!
    # We still resolve to a username and then resolve back to a 
    # userid to make sure the user actually exists on this server.
    # Efficient? No. Works? Yup!
    if username.startswith("<@"):
        uid = username.strip("<@").strip(">")
        username = ctx.message.server.members[uid].name
    
    # Get the ID from the user name
    for member in ctx.message.server.members:
        if member.name == username:
            userid = member.id
    
    # Build our response
    response = ""
    if userid == 0:
        response = "Unknown user " + username
    else:
        try:
            seen = last_seen[userid].strftime('%A, %B %-m at %-I:%M%p')
        except:
            seen = None

        if seen != None:
            response = "Last saw " + username + " on " + seen
        else:
            response = "Never seen " + username

    await bot.say(response)

async def show_xkcd(num: str, channel):
    comic = libxkcd.getComic(num)
    comic.download(output = pwd, outputFile = "XKCD-" + num + ".png", silent = False)
    await bot.send_message(channel, "XKCD #" + num)
    await bot.send_message(channel, comic.getTitle())
    print(str(pwd))
    await bot.send_file(channel, str(pwd) + "/XKCD-" + num + ".png")
    await bot.send_message(channel, comic.getAltText())

async def _watch_xkcd():
    await bot.wait_until_ready()
    
    # Python was getting finnicky about modifying a global int. This is the easiest way around that
    while not bot.is_closed:
        if xkcd_conf['latest_seen_comic'] != libxkcd.getLatestComicNum():
            xkcd_conf['latest_seen_comic'] = libxkcd.getLatestComicNum()
            for channel in watch_list:
                await show_xkcd(str(xkcd_conf['latest_seen_comic']), bot.get_channel(channel))
            save_xkcd_conf()

        await asyncio.sleep(60)

def save_xkcd_conf():
    f = open(WATCH_XKCD_CONF_FILE, 'w')
    f.write(json.dumps(xkcd_conf))
    f.close()

def save_last_seen():
    f = open(LAST_SEEN_FILE, 'w')
    f.write(json.dumps(last_seen, default=str))
    f.close()

def load_last_seen():
    f = open(LAST_SEEN_FILE, 'r')
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
                if str(member.status) == "online":
                    last_seen[member.id] = now
        
        save_last_seen()
        await asyncio.sleep(60)

               
last_seen = load_last_seen()

bot.loop.create_task(_watch_xkcd())
bot.loop.create_task(log_people_seen())
bot.run(token)
