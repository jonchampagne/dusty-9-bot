def init(bot):
    Math(bot)
    return True

def help(ctx):
    s = "MATH: \n"
    s += ctx.bot.command_prefix + "acc: v1,v2,t Calculate acceleration, with V1 (Initial Velocity), V2 (Second Velocity), and time. For velocity, use consistent units\n"

    return s

class Math:
    bot = None

    def _register_commands(self):
        bot = self.bot

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

    def __init__(self, robot):
        self.bot = robot
        self._register_commands()
