import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

from conduit.functions import spliceNick


@conduit.module_loader.add_command("users")
def user_list(data, server):
    users = Connector.session.query(Users).filter(Users.online == 1).all()
    userList = ""
    for user in users:
        userList = userList + " " + spliceNick(user.nick) + " (" + server.getServer(user.server) + ")"
    server.msg(serv_chan, "Online Users:" + userList)