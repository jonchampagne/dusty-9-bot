import random
import dice
from textwrap import wrap

def init(bot):
  Random(bot)
  return True

def help(ctx):
  pref = ctx.bot.command_prefix

  s = "RANDOM: \n"
  s += pref + "flip: Flip a coin\n"
  s += pref + "flip n: Flip n coins\n"
  s += pref + "roll X: Rolls d a die or dice, specified in standard die notation (XdY)\n"
  s += pref + "roll_stats X: Various statistics of a roll specified in standard die notation (XdY)\n"

  return s

def on_ready():
  pass

class Random:
  bot = None

  def _register_commands(self):
    bot = self.bot

    @bot.command()
    async def flip(ctx, count = 1):
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
          if rnum < 0.499:
            outstr += "Heads! "
          elif rnum > 0.501:
            outstr += "Tails! "
          else:
            outstr += "It landed on it's side... "

        splitlength = 1995

        s = wrap(outstr, splitlength)

        for i in s:
          await ctx.send(i)

      except Exception as e:
        await ctx.send("Error: " + str(e))
        print(traceback.format_exc())


    @bot.command()
    async def roll(ctx, dice : str):
      try:
        rolls, limit = map(int, dice.split('d'))
      except Exception:
        await ctx.send('Format has to be in NdN!')
        return

      result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))

      try:
        await ctx.send(result)
      except Exception:
        await ctx.send(sys.exc_info()[0])

    @bot.command()
    async def roll_stats(ctx, dicestr : str):
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
      s  = "Minimum: " + str(minimum) + "\n"
      s += "Maximum: " + str(maximum) + "\n"
      s += "Typical roll: " + str(typical)
      await ctx.send(s)

  def __init__(self, robot):
    self.bot = robot
    self._register_commands()
