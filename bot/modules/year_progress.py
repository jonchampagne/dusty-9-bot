import asyncio
import datetime
from math import floor
from discord import ChannelType

SECONDS_IN_YEAR = 31622400

YEAR_PERCENTAGE_FILE = 'year_percentage.txt'

def init(bot):
    # Disabled by default
    #bot.loop.create_task(year_progress(bot))
    return True

def help(ctx):
    return ""

async def year_progress(bot):
    await bot.wait_until_ready()

    while not bot.is_closed:
        # Read what the latest percentage we've displayed is
        try:
            f = open(YEAR_PERCENTAGE_FILE, 'r')
            latest_perc = int(f.read())
        except (FileNotFoundError, ValueError):
            latest_perc = 0

        # Calculate the percentage of the year past
        now = datetime.datetime.now()
        year_start = datetime.datetime(now.year, 1, 1)
        seconds = (now - year_start).total_seconds()
        perc = floor((seconds / SECONDS_IN_YEAR) * 100)

        if perc < 99 and latest_perc >= 99:
            latest_perc = 0;

        if perc > latest_perc:
            # Print out to all channels the year percentage
            bar = _generate_bar(perc)
            for channel in bot.get_all_channels():
                try:
                    if channel.type == ChannelType.text:
                        await bot.send_message(channel, bar + " " + str(perc) + "%")
                except:
                    print("Error sending message in channel: " + channel.name)

            # Save the percentage so we're not repeating ourselves
            f = open(YEAR_PERCENTAGE_FILE, 'w')
            f.write(str(perc))
            f.close()

        # 61 seconds to add a bit of pseudorandomness to when it actually prints out :P
        await asyncio.sleep(61)

def _generate_bar(percentage):
    length = 15

    filled = round((percentage / 100) * length)

    s = ""
    for i in range(filled):
        s += "▓"
    for i in range (length - filled):
        s += "░"

    return s
