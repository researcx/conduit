#!/usr/bin/env python3
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, ssl
from conduit.functions import html_escape, splice, spliceNick
import time, sys, re

import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

serv_id = int(sys.argv[1])
serv_ip = sys.argv[2]
serv_port = int(sys.argv[3])
serv_nick = sys.argv[4]
serv_chan = sys.argv[5]
serv_owner = sys.argv[6]
serv_secure = int(sys.argv[7])

re_chan = '[&\#][^ ,\x07]{1,200}'
re_nick = '[A-Za-z\[\]\\`_\^\{\|\}][A-Za-z0-9\[\]\\`_\^\{\|\}\-]{0,8}'
re_ident = '[^\r\n@ ]+'
re_privmsg = ':(%s)!(%s)@([A-Za-z0-9\-\./]+) PRIVMSG (%s) :(.*)' % (re_nick, re_ident, re_chan)
re_user = '(%s)!(%s)@([A-Za-z0-9\-\./]+)' % (re_nick, re_ident)


class Conduit(irc.IRCClient):
    nickname = serv_nick
    lastMessage = 0
    onlineUserList = []
    
    def who(self, channel):
        self.sendLine('WHO %s' % channel)

    def userIdentity(self, nick, user, host):
        who_full = nick + "!" + user + "@" + host
        return who_full

    def userMask(self, user, host):
        who_mask = user + "@" + host
        return who_mask

    def matchUser(self, mask1, mask2):
        print(lol)

    def addUser(self, nick, user, host, channel, rank, online):
        checkUsers = Connector.session.query(Users).filter(Users.channel == channel).filter(Users.user == user).filter(Users.host == host).first()
        if not checkUsers:
            newUser = Users(server=serv_id, channel=channel, nick=nick, user=user, host=host, rank=rank, online=online)
            Connector.session.add(newUser)
            Connector.session.commit()
            return 1
        else:
            return 0

    def checkStatus(self, channel):
        onlineUsers = Connector.session.query(Users).filter(Users.channel == channel).all()
        for user in onlineUsers:
            userMask = self.userMask(user.user, user.host)
            if userMask in self.onlineUserList:
                user.online = 1
                Connector.session.commit()
            else:
                user.online = 0
                Connector.session.commit()

    def getServer(self, serv_id):
        currentServer = Connector.session.query(Servers).filter(Servers.id == serv_id).first()
        return currentServer.name

    def irc_RPL_WHOREPLY(self, *nargs):
        who_nick = nargs[1][5]
        who_user = nargs[1][2]
        who_host = nargs[1][3]
        who_channel = nargs[1][1]

        # print(self.userIdentity(who_nick, who_user, who_host))
        # print(self.userMask(who_user, who_host))
        self.onlineUserList.append(self.userMask(who_user, who_host))
 
        if who_nick != serv_nick:
            self.addUser(who_nick, who_user, who_host, who_channel, 0, 1)

    def irc_RPL_ENDOFWHO(self, *nargs):
        self.checkStatus(nargs[1][1])

    def signedOn(self):
        self.join(serv_chan)

    def joined(self, serv_chan):
        self.who(serv_chan)
        l = task.LoopingCall(self.checkMessages)
        l.start(1)

    def privmsg(self, user, channel, message):
        isOwner = user.split('@')[1] in serv_owner
        isCommand = 0

        # Commands
        if isOwner:
            msg = message.split()
            if "!users" in msg[0]:
                isCommand = 1
                users = Connector.session.query(Users).filter(Users.online == 1).all()
                userList = ""
                for user in users:
                    userList = userList + " " + spliceNick(user.nick) + " (" + self.getServer(user.server) + ")"
                self.msg(serv_chan, "Online Users:" + userList)
            if (("!invite" in msg[0]) and (len(msg) == 3 )):
                isCommand = 1
                rank = 1
                rank_name = "user"
                if ((msg[2] == "halfop") or (int(msg[2]) == 10)):
                    rank = 10
                    rank_name = "halfop"
                elif ((msg[2] == "op") or (int(msg[2]) == 100)):
                    rank = 100
                    rank_name = "op"
                userRegex = re.findall(re_user,  msg[1])
                addUser = self.addUser(userRegex[0][0], userRegex[0][1], userRegex[0][2], channel, rank, 0)
                if addUser:
                    self.describe(serv_chan, "invited " +msg[1] + " ("+ rank_name +")")
                else:
                    self.say(serv_chan, msg[1] + " is already in the database")
                

        # Log some messages
        if not isCommand:
            new_message = Messages(server=serv_id, sent=str(serv_id) + ";", channel=channel, sender=user, message=message, type="PRIVMSG")
            Connector.session.add(new_message)
            Connector.session.commit()

    def action(self, user, channel, data):
        new_message = Messages(server=serv_id, sent=str(serv_id) + ";", channel=channel, sender=user, message=data, type="ACTION")
        Connector.session.add(new_message)
        Connector.session.commit()

    def checkMessages(self):
        messages = Connector.session.query(Messages).filter(Messages.server != serv_id).all()
        for message in messages:
            sent =  [int(i) for i in message.sent.split(";") if i]
            if serv_id not in sent:
                sender = message.sender.split("!")[0]
                if message.type == "ACTION":
                    self.msg(message.channel,  spliceNick(sender) + " " + message.message)
                else:
                    self.msg(message.channel, "<" + spliceNick(sender) + "> " + message.message)
                message.sent = message.sent + str(serv_id) + ";"
                Connector.session.commit()

def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = Conduit

    if serv_secure:
        reactor.connectSSL(serv_ip, serv_port, f, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
