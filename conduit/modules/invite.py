import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

from conduit.functions import spliceNick
            
re_user = '(%s)!(%s)@([A-Za-z0-9\-\./]+)' % (re_nick, re_ident)

@conduit.module_loader.add_command("invite")
def invite_user(data, server):            
    msg = data[2].split(" ")
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
    