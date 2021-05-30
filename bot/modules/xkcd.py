import os
import os.path
import json
import xkcd as libxkcd
import asyncio
import config
import discord
from discord.ext import tasks
import tempfile

WATCH_XKCD_CONF_FILE = config.CONFIG_DIR + '/watch_xkcd_conf.json'

bot_prefix = ""

pwd = os.path.dirname(os.path.realpath(__file__)) + "/../.."


def init(bot):
  XKCD(bot)
  return True

def help(ctx):
  s = "XKCD: \n"
  s += ctx.bot.command_prefix + "xkcd n: Pulls up XKCD #n \n"

  return s

def on_ready():
  pass

class XKCD:
  bot = None

  xkcd_conf = None
  watch_list = None
  cachedir = None

  def _register_commands(self):
    bot = self.bot

    @bot.command(pass_context=True)
    async def xkcd(ctx, num: str):
      await self.show_xkcd(num, ctx.message.channel)

    @bot.command(pass_context=True)
    async def watch_xkcd(ctx):
      id = ctx.message.channel.id
      watch_list = self.watch_list
      if id in watch_list:
        watch_list.remove(id)
        message = "Removed channel #" + ctx.message.channel.name + " from XKCD watch list"
      else:
        watch_list.append(id)
        message = "Added channel #" + ctx.message.channel.name + " to XKCD watch list"

      self.save_xkcd_conf()
      await ctx.send(message)

  async def show_xkcd(self, num: str, channel):
    async with channel.typing():
      bot = self.bot
      comic = libxkcd.getComic(num)

      # Prepare to embed the comic
      filename = "XKCD-" + num + ".png"
      filepath = comic.download(output = self.cachedir, outputFile = filename, silent = False)
      file = discord.File(filepath, filename = filename)
      embed = discord.Embed(title = "XKCD #" + num + "\n" + comic.getTitle(), description = "||" + comic.getAltText() + "||")
      embed.set_image(url = "attachment://" + filename)

      await channel.send(file = file, embed = embed)
      # await bot.send_message(channel, comic.getTitle())
      # await bot.send_file(channel, str(pwd) + "/XKCD-" + num + ".png")
      # await bot.send_message(channel, "||" + comic.getAltText() + "||")

  @tasks.loop(seconds = 5)
  async def _watch_xkcd(self):
    bot = self.bot
    xkcd_conf = self.xkcd_conf
    watch_list = self.watch_list

    print("Waiting")
    await bot.wait_until_ready()

    # Python was getting finnicky about modifying a global int. This is the easiest way around that
    while not bot.is_closed:
      print("Checking for new comic")
      if xkcd_conf['latest_seen_comic'] != libxkcd.getLatestComicNum():
        xkcd_conf['latest_seen_comic'] = libxkcd.getLatestComicNum()
        for channel in watch_list:
          await self.show_xkcd(str(xkcd_conf['latest_seen_comic']), bot.get_channel(channel))
        self.save_xkcd_conf()
      if xkcd_conf['latest_seen_whatif'] != libxkcd.getLatestWhatIfNum():
        xkcd_conf['latest_seen_whatif'] = libxkcd.getLatestWhatIfNum()
        whatif = libxkcd.getLatestWhatIf()
        for channel in watch_list:
          message = "New what if!\n" + whatif.getTitle() + "\n" + whatif.getLink()
          await bot.send_message(bot.get_channel(channel), message)
        self.save_xkcd_conf()

  def save_xkcd_conf(self):
    f = open(WATCH_XKCD_CONF_FILE, 'w')
    f.write(json.dumps(self.xkcd_conf))
    f.close()


  def __init__(self,robot):
    self.bot = robot
    bot = self.bot

    # Check if WATCH_XKCD_CONF_FILE exists. If not, create it.
    try:
      xkcd_file = open(WATCH_XKCD_CONF_FILE, 'r')
    except FileNotFoundError:
      xkcd_file_create = open(WATCH_XKCD_CONF_FILE, 'w')
      xkcd_file_create.write("{\"channels\": [], \"latest_seen_comic\": null, \"whatif_channels\": [], \"latest_seen_whatif\": null}")
      xkcd_file_create.close()

    self.xkcd_conf = json.loads(open(WATCH_XKCD_CONF_FILE).read())
    self.watch_list = self.xkcd_conf['channels']

    self.cachedir = tempfile.TemporaryDirectory(prefix = "xkcd-").name

    # Make sure the latest what if is also in the xkcd file
    if 'latest_seen_whatif' not in self.xkcd_conf:
      self.xkcd_conf['latest_seen_whatif'] = 0

    # Register the bot commands
    self._register_commands()
