#!/usr/bin/env python3
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, ssl
from conduit.functions import html_escape, splice, spliceNick
import os, time, sys, re, logging, json, coloredlogs, threading

import conduit.db.connect as Connector
from conduit.db.messages import Messages
from conduit.db.users import Users

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
        self.server_id = None
        self.config = None
        self.nickname = None
        self.channels = None
        self.owner = None
        self.blacklist = None
        self.commands = None
        self.command_regex = None
        self.connect_commands = []
        self.lastMessage = 0
        self.onlineUserList = {}

    def connectionMade(self):
        logging.debug(f'connectionMade called.')
        
        # so, my previous attempt of obtaining an index was to create an array assuming that each client would match a config instance,
        # but the issue with that was that, since if multiple clients were launched to different servers, one could finish before the other,
        # meaning the socket address and port would've been correct, but the config loaded would not have been since one would finish before the other.
        # this would've been fine if twisted had let me do it upon __init__, but since connectionMade is when self.factory has a reference, i must overcome it by:
        # * getting the port and original hostname of the connection
        # * comparing those against the config itself
        # * if there's more than one instance of the same hostname:port,
        # * check it against pre-existing conduits to see if it has been loaded as a config yet
        # * if it has, select the next available server config
        # * then break the loop for searching
        # i question whether self.factory.multiplexer.conduits is needed at all anymore, but... if you want to do an action on all clients, that's still a way to do it (i guess?)
        self._peer = self.transport.getPeer()
        self.ip = self._peer.host
        self.port = self._peer.port
        self.hostname = self.transport.connector.getDestination()
        potential_config = None
        for server in self.factory.multiplexer.config.data["servers"]:
            if server["endpoint"] == self.hostname and server["port"] == self.port:
                for conduit_instance in self.factory.multiplexer.conduits:
                    if server["id"] != conduit_instance.server_id:
                        potential_config = server
                        break
        self.config = potential_config

        self.factory.multiplexer.conduits.append(self)
        logging.debug(f'config id: ' + str(self.config["id"]))
        self.server_id = self.config["id"]
        logging.debug(f'config server: ' + self.config["name"])
        logging.debug(f'config nick: ' + self.config["nick"])
        self.nickname = self.config["nick"]
        logging.debug(f'config username: ' + self.config["user"])
        self.username = self.config["user"]
        logging.debug(f'config channels: ' + str(self.config["channels"]))
        self.channels = self.config["channels"]
        logging.debug(f'config owner: ' + str(self.config["owner"]))
        self.owner = self.config["owner"]
        logging.debug(f'config blacklist: ' + str(self.config["blacklist"]))
        self.blacklist = self.config["blacklist"]
        self.connect_commands = self.config["commands"]
        self.commands = self.factory.multiplexer.commands
        logging.debug(f'config commands: ' + str(self.commands))
        for blacklisted_command in self.blacklist:
            logging.debug(f'blacklisted command: ' + str(self.commands[blacklisted_command]))
            del self.commands[blacklisted_command]
        self.command_regex = re.compile("^\!(\w+)")
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
        check_users = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).first()
        if not check_users:
            new_user = Users(server=self.server_id, channel=channel, nick=nick, user=user, host=host, rank=rank, online=online)
            Connector.session.add(new_user)
            Connector.session.commit()
            return 1
        else:
            return 0

    def change_rank(self, nick, user, host, channel, rank):
        logging.debug(f'change_rank called.')
        check_users = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).filter(Users.rank != rank).first()
        if check_users:
            check_users.rank = rank
            Connector.session.commit()
            return check_users
        else:
            return 0

    def check_rank(self, nick, user, host, channel):
        logging.debug(f'check_rank called.')
        check_users = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).first()
        if check_users:
            logging.debug(str(check_users.nick) + "'s rank is: " + str(check_users.rank))
            if check_users.rank < 10:
                logging.debug(str(check_users.nick) + "'s rank is: " + str(check_users.rank) + ", demoting from halfop")
                self.mode(channel, False, 'h', limit=None, user=nick, mask=None)
            if check_users.rank < 100:
                logging.debug(str(check_users.nick) + "'s rank is: " + str(check_users.rank) + ", demoting from op")
                self.mode(channel, False, 'o', limit=None, user=nick, mask=None)
            if check_users.rank >= 10:
                logging.debug(str(check_users.nick) + "'s rank is: " + str(check_users.rank) + ", promoting to halfop")
                self.mode(channel, True, 'h', limit=None, user=nick, mask=None)
            if check_users.rank >= 100:
                logging.debug(str(check_users.nick) + "'s rank is: " + str(check_users.rank) + ", promoting to op")
                self.mode(channel, True, 'o', limit=None, user=nick, mask=None)
        return 0


    def check_status(self, channel):
        logging.debug(f'check_status called.')
        onlineUsers = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.channel == channel).filter(Users.server == self.server_id).all()
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
        for serverDict in self.factory.multiplexer.config.data["servers"]:
            if serverDict["id"] == server_id:
                return serverDict
        return "?"

    def signedOn(self):
        logging.debug(f'signedOn called.')
        for connect_command in self.connect_commands:
            logging.debug(f'called command: ' + connect_command)
            self.sendLine(connect_command)
        for channel in self.channels:
            self.onlineUserList[channel] = []
            self.join(channel)
            logging.debug(self.onlineUserList[channel])

    def userJoined(self, user, channel):
        userRegex = re.findall(re_user,  user)
        self.check_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], channel)

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
            logging.debug(f'isOwner: ' + user.split('!')[1] + ' is ' + self.owner)
            logging.debug(f'is ' + str(match_object.group(1))  + ' in ' + str(self.commands) + '?')
            if match_object.group(1) in self.commands:
                logging.debug(f'matched: ' + str(match_object.group(1))  + ' is in ' + str(self.commands))
                self.commands[match_object.group(1)]((user, channel, message), self)
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

    ## Twisted overrides
    def irc_RPL_WHOREPLY(self, *nargs):
        logging.debug(f'irc_RPL_WHOREPLY called.')
        who_nick = nargs[1][5]
        who_user = nargs[1][2]
        who_host = nargs[1][3]
        who_channel = nargs[1][1]
        who_modes = nargs[1][6]
        # print(build_hostmask(who_nick, who_user, who_host))
        # print(build_nickless_hostmask(who_user, who_host))
        
        if who_channel in self.channels:
            self.onlineUserList[who_channel].append(build_nickless_hostmask(who_user, who_host))
            logging.debug(self.onlineUserList[who_channel])
        else:
            self.onlineUserList[who_channel] = [build_nickless_hostmask(who_user, who_host)]
            logging.debug(self.onlineUserList[who_channel])
 
        logging.debug(f"comparing " + who_nick + " to " + self.nickname)
        if who_nick != self.nickname:
            logging.debug(who_nick + " is not " + self.nickname)
            self.add_user(who_nick, who_user, who_host, who_channel, 0, 1)

    def irc_RPL_ENDOFWHO(self, *nargs):
        logging.debug(f'irc_RPL_ENDOFWHO called.')
        self.check_status(nargs[1][1])

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
