#!/usr/bin/env python3
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, ssl
from conduit.functions import html_escape, splice, spliceNick
import os, time, sys, re, logging, json, coloredlogs, threading

import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

import conduit.module_loader

def build_hostmask(nick, user, host):
        who_full = nick + "!" + user + "@" + host
        return who_full

def build_nickless_hostmask(user, host):
        who_mask = user + "@" + host
        return who_mask

class Conduit(irc.IRCClient):
    logging.debug(f'Conduit called.')
    def __init__(self):
        self.index = None
        self.config = None
        self.nickname = None
        self.server_id = None
        self.channels = None
        self.owner = None
        self.blacklist = None
        self.commands = None
        self.command_regex = None
        self.lastMessage = None
        self.onlineUserList = None

    def connectionMade(self):
        logging.debug(f'connectionMade called.')
        self.factory.multiplexer.conduits.append(self)
        self.index = self.factory.multiplexer.conduits.index(self)
        self.config = self.factory.multiplexer.config.data["servers"][self.index]
        logging.debug(f'config nick: ' + self.config["nick"])
        self.nickname = self.config["nick"]
        logging.debug(f'config id: ' + str(self.config["id"]))
        self.server_id = self.config["id"]
        logging.debug(f'config channels: ' + str(self.config["channels"]))
        self.channels = self.config["channels"]
        logging.debug(f'config owner: ' + str(self.config["owner"]))
        self.owner = self.config["owner"]
        logging.debug(f'config blacklist: ' + str(self.config["blacklist"]))
        self.blacklist = self.config["blacklist"]
        self.commands = self.factory.multiplexer.commands
        logging.debug(f'config commands: ' + str(self.commands))
        for blacklisted_command in self.blacklist:
            logging.debug(f'blacklisted command: ' + str(self.commands[blacklisted_command]))
            del self.commands[blacklisted_command]
        self.command_regex = re.compile("^\!(\w+)")
        self.lastMessage = 0
        self.onlineUserList = {}
        logging.debug(f'got to the end of connectionMade')
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        logging.debug(f'connectionLost called.')
        self.factory.multiplexer.conduits.remove(self)

    def who(self, channel):
        logging.debug(f'who called.')
        self.sendLine('WHO %s' % channel)

    def match_user(self, mask1, mask2):
        logging.debug(f'match_user called.')
        pass

    def add_user(self, nick, user, host, channel, rank, online):
        logging.debug(f'add_user called.')
        checkUsers = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).first()
        if not checkUsers:
            newUser = Users(server=self.server_id, channel=channel, nick=nick, user=user, host=host, rank=rank, online=online)
            Connector.session.add(newUser)
            Connector.session.commit()
            return 1
        else:
            return 0

    def check_status(self, channel):
        logging.debug(f'check_status called.')
        onlineUsers = Connector.session.query(Users).filter(Users.channel == channel).all()
        for user in onlineUsers:
            userMask = build_nickless_hostmask(user.user, user.host)
            if userMask in self.onlineUserList[channel]:
                user.online = 1
                Connector.session.commit()
            else:
                user.online = 0
                Connector.session.commit()

    def get_server(self, server_id):
        logging.debug(f'get_server called.')
        for server in self.config.data["servers"]:
            if server["id"] == server["name"]:
                print(server["name"])
                return server["name"]
        return 0

    def irc_RPL_WHOREPLY(self, *nargs):
        logging.debug(f'irc_RPL_WHOREPLY called.')
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
            self.add_user(who_nick, who_user, who_host, who_channel, 0, 1)

    def irc_RPL_ENDOFWHO(self, *nargs):
        logging.debug(f'irc_RPL_ENDOFWHO called.')
        self.check_status(nargs[1][1])

    def signedOn(self):
        logging.debug(f'signedOn called.')
        for channel in self.channels:
            self.join(channel)

    def joined(self, channel):
        logging.debug(f'joined called.')
        self.who(channel)
        l = task.LoopingCall(self.check_messages)
        l.start(1)

    def privmsg(self, user, channel, message):
        logging.debug(f'privmsg called.')
        match_object = self.command_regex.match(message)
        if match_object:
            # command logic
            isOwner = user.split('!')[1] in self.owner
            if match.group(0) in self.commands:
                self.commands[match.group(0)]((user, channel, message), self)
        else:
            self.save_message(user, channel, message, "PRIVMSG")

    def action(self, user, channel, data):
        logging.debug(f'action called.')
        self.save_message(user, channel, data, "ACTION")

    def save_message(self, user, channel, message, type):
        logging.debug(f'save_message called.')
        new_message = Messages(server=self.server_id, sent=str(self.server_id) + ";", channel=channel, sender=user, message=message, type=type)
        Connector.session.add(new_message)
        Connector.session.commit()

    def check_messages(self):
        #logging.debug(f'check_messages called.')
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

class ConduitFactory(protocol.ReconnectingClientFactory):
    logging.debug(f'ConduitFactory called.')
    def __init__(self, multiplexer):
        self.multiplexer = multiplexer
        self.protocol = Conduit

class Config(object):
    logging.debug(f'Config called.')
    def __init__(self, path):
        try:
            with open(path) as config_file:
                self.data = json.load(config_file)
        except:
            logging.error(f"Could not load the config from {path}.")
        else:
            logging.info(f"Successfully loaded the config from {path}.")

class ConduitMultiplexer():
    logging.debug(f'ConduitMultiplexer called.')
    def __init__(self):
        logging.debug(f'ConduitMultiplexer __init__.')
        self.conduits = []
        self.config = None
        self.commands = None

    def start(self):
        logging.debug(f'ConduitMultiplexer start.')
        self.config = Config(os.path.dirname(os.path.abspath( __file__ )) + "/data/bot.cfg")
        conduit.module_loader.base_dir = os.path.dirname(os.path.abspath( __file__ ))
        conduit.module_loader.import_dir("./modules/")
        self.commands = conduit.module_loader.commands
        f = ConduitFactory(self)
        for server in self.config.data["servers"]:
            security_str = "secure" if server["secure"] else "insecure"
            logging.info(f'Attempting {security_str} connection to {server["endpoint"]}:{server["port"]}.')
            if server["secure"]:
                logging.debug(f'Connecting with SSL.')
                reactor.connectSSL(server["endpoint"], server["port"], f, ssl.ClientContextFactory())
            else:
                logging.debug(f'Connecting with TCP.')
                reactor.connectTCP(server["endpoint"], server["port"], f)
        logging.debug(f'Running reactor.')
        reactor.run()


def main():
    logging.debug(f'main called.')
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
    logging.debug(f'__main__ called.')
    main()
