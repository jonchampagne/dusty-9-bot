import feedparser
import json
import validators
import traceback
import datetime
import urllib

RSS_CONFIG_FILE = "rss_config.json"

def init(bot):
    FeedReader(bot)
    return True

def help(ctx):
    prefix = ctx.bot.command_prefix
    s = "RSS\n"
    s += prefix + "add_rss_feed url: Add an RSS feed to be posted by the bot\n"
    s += prefix + "remove_rss_feed url: Remove an RSS feed previously added to this channel\n"
    s += prefix + "show_rss_feeds: List out the RSS feeds currently added to this channel\n"
    return s

class FeedReader:
    bot = None
    config = None

    def _register_commands(self):

        @self.bot.command(pass_context=True)
        async def add_rss_feed(ctx, url: str):
            # Verify we got a proper URL
            if not validators.url(url):
                await self.bot.say("Invalid URL")
                return

            # Try to parse the feed, or crap out
            try:
                d = feedparser.parse(url)
            except Exception as e:
                print(traceback.format_exc())
                await self.bot.say(str(e))
                return

            # Typically happens when the URL is bad
            if d.bozo and type(d.bozo_exception) is urllib.error.URLError:
                await self.bot.say("Bad feed")
                return

            # I heard you like feeds, so I make sure there's a feed in all our feeds
            if 'feed' not in d:
                await self.bot.say("Bad feed")
                return

            # Veryfy it's some iteration of RSS we got back
            if not d.version.startswith('rss'):
                await self.bot.say("Error: Couldn't identify RSS version.")
                return

            # Fall back to the URL for the title if need be
            if 'title' in d.feed:
                title = d.feed['title']
            else:
                title = url

            # Some feeds have descriptions, some don't.
            if 'description' in d.feed:
                description = d.feed['description']
            else:
                description = None

            # If we're already watching the feed, check if it's for this channel or another one.
            # If it's this channel, crap out. If it's another channel, just add it to the list of
            # channels output to when the feed gets an update. #efficiency
            if url in self.config['feeds']:
                if ctx.message.channel.id in self.config['feeds'][url]['channels']:
                    await self.bot.say("Feed already registered to channel #" + ctx.message.channel.name)
                    return
                else:
                    self.config['feeds'][url]['channels'].append(ctx.message.channel.id)
            else:
                message = "Adding feed: \n"
                message += title
                if description is not None: message += "\n" + description
                await self.bot.say(message)

                # Dear god... But hey, works fine.
                self.config['feeds'][url] = {}
                self.config['feeds'][url]['channels'] = []
                self.config['feeds'][url]['channels'].append(ctx.message.channel.id)
                self.config['feeds'][url]['title'] = title
                self.config['feeds'][url]['description'] = description
                self.config['feeds'][url]['latest_seen'] = datetime.datetime.now()

            self._watch_feed(url)

            self.save_config()

        @self.bot.command(pass_context=True)
        async def remove_rss_feed(ctx, *args):
            url = ""
            for arg in args:
                url += arg + " "
            url = url.strip()


            if not url:
                return

            # url is not a very good variable name here...
            # Essentially if we get a non-url, we check to see if it exactly matches
            # a title of a feed, and if so set url to the actual url of the feed and
            # continue on. Otherwise just error out
            if not validators.url(url):
                for feed_url, feed in self.config['feeds'].items():
                    if feed['title'] == url:
                        something_found = True
                        url = feed_url
                        break
                if not something_found:
                    await self.bot.say("Error: Feed not registered. ")
                    return
                else: something_found = None

            # Verify the URL is registered with this channel
            if url not in self.config['feeds'] or ctx.message.channel.id not in self.config['feeds'][url]['channels']:
                await self.bot.say("Error: Feed not registered.")
                return

            # Save the title for later
            title = self.config['feeds'][url]['title']

            # Remove the feed
            self.config['feeds'][url]['channels'].remove(ctx.message.channel.id)

            # If there's no other channels using the feed, totally remove it.
            if not self.config['feeds'][url]['channels']:
                del self.config['feeds'][url]

            self.save_config()

            await self.bot.say("Removed feed " + title)

        @self.bot.command(pass_context=True)
        async def show_rss_feeds(ctx):
            # Simple loop through of the feeds and print out the ones that are
            # applicable to the calling channel.
            message = ""
            for url, feed in self.config['feeds'].items():
                if ctx.message.channel.id in feed['channels']:
                    something_found = True
                    if feed['title'] == url:
                        message += "URL: " + url + "\n"
                    else:
                        message += "Title: " + feed['title'] + "\n"
                    if feed['description']:
                        message += "Description: " + feed['description'] + "\n"
                    message += "\n"

            if not something_found:
                message += "No feeds registered"

            await self.bot.say(message)

    def _watch_feed(self, url):
        print("WARNING: watch_feed not implemented. " + url)

    def save_config(self):
        try:
            f = open(RSS_CONFIG_FILE, 'w')
            f.write(json.dumps(self.config, default=str, indent=1, sort_keys=True))
            f.close()
            return True
        except:
            return False

    def __init__(self, robot):
        self.bot = robot

        try:
            f = open(RSS_CONFIG_FILE, 'r')
            self.config = json.loads(f.read())
            f.close()
        except FileNotFoundError as e:
            print("WARNING: Generating new RSS config file")
            self.config = {}

        # A pretty bulletproof way of implementing future config options, assuming they can have a default value
        if 'global' not in self.config:
            self.config['global'] = {}
        if 'feeds' not in self.config:
            self.config['feeds'] = {}

        if not self.save_config():
            raise Exception('Error saving rss config file ' + RSS_CONFIG_FILE)

        self._register_commands()

        for url, feed in self.config['feeds'].items():
            self._watch_feed(url)

