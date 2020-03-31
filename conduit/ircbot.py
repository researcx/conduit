#!/usr/bin/env python3
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, ssl
from conduit.functions import html_escape, splice, spliceNick
import time, sys, re, logging, json, coloredlogs

import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

import conduit.module_loader

re_chan = '[&\#][^ ,\x07]{1,200}'
re_nick = '[A-Za-z\[\]\\`_\^\{\|\}][A-Za-z0-9\[\]\\`_\^\{\|\}\-]{0,8}'
re_ident = '[^\r\n@ ]+'
re_privmsg = ':(%s)!(%s)@([A-Za-z0-9\-\./]+) PRIVMSG (%s) :(.*)' % (re_nick, re_ident, re_chan)
re_user = '(%s)!(%s)@([A-Za-z0-9\-\./]+)' % (re_nick, re_ident)

def build_hostmask(nick, user, host):
        who_full = nick + "!" + user + "@" + host
        return who_full

def build_nickless_hostmask(user, host):
        who_mask = user + "@" + host
        return who_mask

class Conduit(irc.IRCClient):
    def __init__(self):
        self.factory.multiplexer.conduits.append(self)
        self.index = self.factory.multiplexer.conduits.index(self)
        self.config = self.factory.multiplexer.config["servers"][self.index]
        self.nickname = self.config["nick"]
        self.server_id = self.config["id"]
        self.channels = self.config["channel"]
        self.owner = self.config["owner"]
        self.blacklist = self.config["blacklist"]
        self.commands = self.factory.multiplexer.commands
        for blacklisted_command in self.blacklist:
            del self.commands[blacklisted_command]
        self.command_regex = re.compile("^\!(\w+)")
        self.lastMessage = 0
        self.onlineUserList = {}
    
    def connectionMade(self):
        try:
            self.index = self.factory.multiplexer.conduits.index(self)
        except ValueError:
            self.factory.multiplexer.conduits.append(self)
        
    def connectionLost(self):
        self.factory.multiplexer.conduits.remove(self)

    def who(self, channel):
        self.sendLine('WHO %s' % channel)

    def matchUser(self, mask1, mask2):
        pass

    def addUser(self, nick, user, host, channel, rank, online):
        checkUsers = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).first()
        if not checkUsers:
            newUser = Users(server=self.server_id, channel=channel, nick=nick, user=user, host=host, rank=rank, online=online)
            Connector.session.add(newUser)
            Connector.session.commit()
            return 1
        else:
            return 0

    def checkStatus(self, channel):
        onlineUsers = Connector.session.query(Users).filter(Users.channel == channel).all()
        for user in onlineUsers:
            userMask = build_nickless_hostmask(user.user, user.host)
            if userMask in self.onlineUserList[channel]:
                user.online = 1
                Connector.session.commit()
            else:
                user.online = 0
                Connector.session.commit()

    def getServer(self, server_id):
        currentServer = Connector.session.query(Servers).filter(Servers.id == server_id).first()
        return currentServer.name

    def irc_RPL_WHOREPLY(self, *nargs):
        who_nick = nargs[1][5]
        who_user = nargs[1][2]
        who_host = nargs[1][3]
        who_channel = nargs[1][1]

        # print(build_hostmask(who_nick, who_user, who_host))
        # print(build_nickless_hostmask(who_user, who_host))
        if who_channel in onlineUserList:
            self.onlineUserList[who_channel].append(build_nickless_hostmask(who_user, who_host))
        else:
            self.onlineUserList[who_channel] = [build_nickless_hostmask(who_user, who_host)]
 
        if who_nick != serv_nick:
            self.addUser(who_nick, who_user, who_host, who_channel, 0, 1)

    def irc_RPL_ENDOFWHO(self, *nargs):
        self.checkStatus(nargs[1][1])

    def signedOn(self):
        for channel in self.channels:
            self.join("channels")

    def joined(self, channel):
        self.who(channel)
        l = task.LoopingCall(self.checkMessages)
        l.start(1)

    def privmsg(self, user, channel, message):
        match_object = self.command_regex.match(message)
        if match_object:
            # command logic
            isOwner = user.split('@')[1] in serv_owner
            if match.group(0) in self.commands:
                self.commands[match.group(0)]((user, channel, message), self)
        else:
            new_message = Messages(server=self.server_id, sent=str(self.server_id) + ";", channel=channel, sender=user, message=message, type="PRIVMSG")
            Connector.session.add(new_message)
            Connector.session.commit()

    def action(self, user, channel, data):
        new_message = Messages(server=self.server_id, sent=str(self.server_id) + ";", channel=channel, sender=user, message=data, type="ACTION")
        Connector.session.add(new_message)
        Connector.session.commit()

    def checkMessages(self):
        messages = Connector.session.query(Messages).filter(Messages.server != self.server_id).all()
        for message in messages:
            sent =  [int(i) for i in message.sent.split(";") if i]
            if self.server_id not in sent:
                sender = message.sender.split("!")[0]
                if message.type == "ACTION":
                    self.msg(message.channel,  spliceNick(sender) + " " + message.message)
                else:
                    self.msg(message.channel, "<" + spliceNick(sender) + "> " + message.message)
                message.sent = message.sent + str(self.server_id) + ";"
                Connector.session.commit()

class ConduitFactory(ReconnectingClientFactory):
    def __init__(self, multiplexer):
        self.multiplexer = multiplexer
        self.protocol = Conduit

    def startedConnecting(self, transport):
        pass
    
    def clientConnectionFailed(self, transport, reason):
        pass
    
    def clientConnectionLost(self, transport, reason):
        pass

class Config(object):
    def __init__(self, path):
        try:
            with open(path) as config_file:
                self.data = json.loads(config_file)
        except:
            logging.error(f"Could not load the config from {path}.")
        else:
            logging.info(f"Successfully loaded the config from {path}.")

class ConduitMultiplexer(Object):
    def __init__(self):
        self.conduits = []
        self.config = None
        self.commands = None

    def start(self):
        self.config = Config("data/bot.cfg")
        conduit.module_loader.import_dir("modules/")
        self.commands = conduit.module_loader.commands
        f = protocol.ConduitFactory()
        for server in self.config.data["servers"]:
            security_str = "secure" if server["secure"] else "insecure"
            logging.info(f"Attempting {security_str} connection to {server["endpoint"]}:{server["port"]}.")
            if server["secure"]:
                reactor.connectSSL(server["endpoint"], server["port"], f, ssl.ClientContextFactory())
            else:
                reactor.connectTCP(server["endpoint"], server["port"], f)
        reactor.run()


def main():
    threading.current_thread().name = 'Conduit'
    # Sets up a debug level logger that overwrites the file
    logging.basicConfig(level=logging.DEBUG,filemode="w")
    logFormatter = logging.Formatter("[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    # Remove the default logger.
    rootLogger.handlers = []
    # Hook the logger up to the file "server.log"
    fileHandler = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "server.log"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    # Hook the logger up to the console
    coloredlogs.install(level='DEBUG',fmt="[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s")
    conduitmx = ConduitMultiplexer()
    conduitmx.start()

if __name__ == "__main__":
    main()
