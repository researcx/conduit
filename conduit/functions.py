from threading import Timer

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

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)