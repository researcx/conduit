#!/usr/bin/env python3
import re, sys

re_chan = '[&\#][^ ,\x07]{1,200}'
re_nick = '[A-Za-z\[\]\\`_\^\{\|\}][A-Za-z0-9\[\]\\`_\^\{\|\}\-]{0,8}|\*+'
re_ident = '[^\r\n@ ]+'
re_privmsg = ':(%s)!(%s)@([A-Za-z0-9\-\./]+) PRIVMSG (%s) :(.*)' % (re_nick, re_ident, re_chan)
re_user = '(%s)!(%s)@([A-Za-z0-9\-\./]+|\*+.*)' % (re_nick, re_ident)

sender = sys.argv[1]

found = re.findall(re_user, sender)

nick = found[0][0]
user = found[0][1]
host = found[0][2]

print(nick)
print(user)
print(host)