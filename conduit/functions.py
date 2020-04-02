from threading import Timer

re_chan = '[&\#][^ ,\x07]{1,200}'
re_nick = '[A-Za-z\[\]\\`_\^\{\|\}][A-Za-z0-9\[\]\\`_\^\{\|\}\-]{0,8}'
re_ident = '[^\r\n@ ]+'
re_privmsg = ':(%s)!(%s)@([A-Za-z0-9\-\./]+) PRIVMSG (%s) :(.*)' % (re_nick, re_ident, re_chan)
re_user = '(%s)!(%s)@([A-Za-z0-9\-\./]+)' % (re_nick, re_ident)

html_escape_table = {
        "'":'&#39;',
        '"':'&quot;',
        '>':'&gt;',
        '<':'&lt;',
        '&':'&amp;'
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def splice(a,b,c,d=None):
    if isinstance(b,(list,tuple)):
        return a[:b[0]]+c+a[b[1]:]
    return a[:b]+d+a[c:]

def spliceNick(nick):
    return splice(nick,(1,1),'\u200B')

def build_hostmask(nick, user, host):
        who_full = nick + "!" + user + "@" + host
        return who_full

def build_nickless_hostmask(user, host):
        who_mask = user + "@" + host
        return who_mask

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)