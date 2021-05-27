import json
import datetime
import asyncio
import config

LAST_SEEN_FILE = config.CONFIG_DIR + '/last_seen.json'

bot_prefix = ""

def init(bot):
  LastSeen(bot)
  bot_prefix = bot.command_prefix
  print(bot_prefix)

  return True

def help(ctx):
  s = "LAST SEEN: \n"
  s += ctx.bot.command_prefix + "last_seen <username>: When was <username> last online?\n"

  print(bot_prefix)

  return s

def on_ready():
  pass

class LastSeen:
  bot = None

  def load_last_seen(self):
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

  def save_last_seen(self):
    f = open(LAST_SEEN_FILE, 'w')
    f.write(json.dumps(self.last_seen, default=str))
    f.close()

  def _register_commands(self):
    bot = self.bot

    @bot.command(pass_context=True)
    async def last_seen(ctx, *args):
      # Spaces deliminate args. Gather them all up into a username.
      username = ""
      for arg in args:
        username += arg + " "
      username = username.strip().lower()

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
        for member in list(ctx.message.channel.members):
          if member.id == uid:
            username = member.name.lower()
            break

      # Get the ID from the user name
      for member in ctx.message.channel.members:
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
          seen = self.last_seen[userid].strftime('%A, %B %d at %I:%M%p')
        except Exception as e:
          print(e)
          seen = None

        if seen != None:
          response = "Last saw " + username + " on " + seen
        else:
          response = "Never seen " + username

      await ctx.send(response)

  async def log_people_seen(self):
    print('Logging people seen')
    bot = self.bot

    await bot.wait_until_ready()

    while not bot.is_closed():
      await asyncio.sleep(1)
      
      now = datetime.datetime.now()
      for server in bot.guilds:
        for member in server.members:
          if str(member.status) != "offline":
            self.last_seen[member.id] = now
        await asyncio.sleep(5)

      self.save_last_seen()

  def __init__(self, robot):
    self.bot = robot
    bot = self.bot

    self._register_commands()

    self.last_seen = self.load_last_seen()
    bot.loop.create_task(self.log_people_seen())



