#!/usr/bin/env python

import pydelicious
import re
import string
import sys
import time
import urllib

from ircbot import SingleServerIRCBot
from drop_privileges import drop_privileges

NICK = 'xxxxxxxx'
DELICIOUS_LOGIN = 'xxxxxxxxx'
DELICIOUS_PASS = 'xxxxxxxxx'

RE_EXTRACT_NICK = re.compile(r'[^\s\!]*')
RE_URL_WITH_TAGS = re.compile('^' + NICK + '[:>,]?\s*(?P<url>([a-z]+\://)?(?P<host>[a-zA-Z0-9\.\-]+)(/\S*)?)\s+\/{2}\s*(?P<tags>\S+(\s+[^\>]+)*)(\s*\>\>\s*(?P<comment>.*))?\s*$')
RE_HELP_NEEDED = re.compile(NICK + '[:>,]?\s+(-)*h(elp)?')
RE_TAG_QUERY = re.compile('^' + NICK + '[:>,]?\s*\/{2}\s*(?P<tag>\S+)\s*\?$')

class TestBot(SingleServerIRCBot):
    """Small extension to the demo IRC bot.

    This bot reacts on messages that look like:

    url //tag tag tag

    and posts this url to del.icio.us/koalicious
    """
    def __init__(self,
                 channel='#koala',
                 nick=NICK,
                 server='irc.epitech.eu',
                 port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        """Called if the nickname is taken.
        """
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """Called when the connexion is established.

        Joins the channel.
        """
        c.join(self.channel)
        print 'Joined channel ' + self.channel

    def on_pubmsg(self, c, e):
        """Callback on public (i.e. on channel) messages

        If this looks like an url with tags, we submit it to del.icio.us.
        The user is notified of the success/failure of this event.
        """
        nick = RE_EXTRACT_NICK.search(e.source()).group(0)
        message = e.arguments()[0]
        match = RE_URL_WITH_TAGS.match(message)
        if match:
            self._add_link(c, e, match)
        elif RE_HELP_NEEDED.match(message):
            self._get_help(c, e)
        elif RE_TAG_QUERY.match(message):
            self._tag_query(c, e)

    def _add_link(self, c, e, match):
        nick = RE_EXTRACT_NICK.search(e.source()).group(0)
        tags = match.group('tags')
        url = match.group('url')
        comment = match.group('comment')
        print comment
        if comment is None:
            comment = ''
        comment = '[%s]' % comment
        # Connects to del.icio.us
        try:
            print 'Submitted by ' + nick + ' ' + comment
            delicious = pydelicious.DeliciousAPI(DELICIOUS_LOGIN, DELICIOUS_PASS)
            delicious.posts_add(
                url=url,
                description=url,
                extended='Submitted by ' + nick + ' ' + comment,
                tags=tags
                )
            c.privmsg(nick, 'Successully logged "%s". Thanks !' % url)
            print 'Successully logged "%s". Thanks !' % url
        except pydelicious.DeliciousItemExistsError:
            c.privmsg(nick, '"%s" has already been submitted.' % url)
        except:
            c.privmsg(nick, 'Sorry, I couldn\'t log "%s". I\'m just a dumb bot.' % url)
        time.sleep(1)

    def _tag_query(self, c, e):
        tag = RE_TAG_QUERY.match(e.arguments()[0]).group('tag')
        c.privmsg(e.target(), '%(tag)s: http://delicious.com/koalicious/%(url)s' % {'tag': tag,
                                                                                      'url': urllib.quote(tag)})

    def _get_help(self, c, e):
        c.privmsg(e.target(), 'This is a IRC-to-delicious bot. To bookmark a link, use the following syntax:')
        c.privmsg(e.target(), NICK + ': http://www.google.com/ //dieu,rtfm,google')
        c.privmsg(e.target(), 'Links are pasted here: http://delicious.com/koalicious')

    def get_version(self):
        """Returns the bot version.

        Used when answering a CTCP VERSION request.
        """
        return "Koalicious"


def main():
    if not drop_privileges('nobody', 'nogroup'):
        print 'Unable to drop privileges. Please run as root:root or nobody:nogroup'
        sys.exit(-1)
    bot = TestBot()
    bot.start()


if __name__ == '__main__':
    main()
