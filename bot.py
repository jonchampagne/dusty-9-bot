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

bot = commands.Bot(command_prefix = '!', case_insensitive = True)
server = None
pwd = os.path.dirname(os.path.realpath(__file__))

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

async def show_xkcd(num: str, channel):
    comic = libxkcd.getLatestComic()
    comic.download(output = pwd, outputFile = "XKCD-" + num + ".png", silent = False)
    await bot.send_message(channel, "XKCD #" + num)
    await bot.send_message(channel, comic.getTitle())
    print(str(pwd))
    await bot.send_file(channel, str(pwd) + "/XKCD-" + num + ".png")
    await bot.send_message(channel, comic.getAltText())

async def watch_xkcd():
    await bot.wait_until_ready()
    
    # Jaysee test server #general
    channel_id = "425450494736203791"
    channel = discord.Object(id=channel_id) 

    i = 0
    
    while not bot.is_closed: 
        if i != libxkcd.getLatestComicNum():
            i = libxkcd.getLatestComicNum()
            await show_xkcd(str(i), channel)
        await asyncio.sleep(60)


bot.loop.create_task(watch_xkcd())
bot.run(token)
