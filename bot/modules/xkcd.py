import os
import os.path
import json
import xkcd as libxkcd
import asyncio

WATCH_XKCD_CONF_FILE = 'watch_xkcd_conf.json'

xkcd_conf = json.loads(open(WATCH_XKCD_CONF_FILE).read())
watch_list = xkcd_conf['channels']

bot_prefix = ""

def init(bot):
    XKCD(bot)
    return True

def help(ctx):
    s = "XKCD: \n"
    s += ctx.bot.command_prefix + "xkcd n: Pulls up XKCD #n \n"

    return s

class XKCD:
    bot = None

    def _register_commands(self):
        bot = self.bot

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

    async def show_xkcd(num: str, channel):
        comic = libxkcd.getComic(num)
        comic.download(output = pwd, outputFile = "XKCD-" + num + ".png", silent = False)
        await bot.send_message(channel, "XKCD #" + num)
        await bot.send_message(channel, comic.getTitle())
        await bot.send_file(channel, str(pwd) + "/XKCD-" + num + ".png")
        await bot.send_message(channel, "||" + comic.getAltText() + "||")

    async def _watch_xkcd(self):
        bot = self.bot

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


    def __init__(self,robot):
        self.bot = robot
        bot = self.bot

        # Check if WATCH_XKCD_CONF_FILE exists. If not, create it.
        try:
            xkcd_file = open(WATCH_XKCD_CONF_FILE, 'r')
        except FileNotFoundError:
            xkcd_file_create = open(WATCH_XKCD_CONF_FILE, 'w')
            xkcd_file_create.write("{\"channels\": [], \"latest_seen_comic\": null}")
            xkcd_file_create.close()

        # Register the watch_xkcd functionality
        bot.loop.create_task(self._watch_xkcd())

        # Register the bot commands
        self._register_commands()
