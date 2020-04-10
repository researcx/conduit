import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users

from conduit.functions import spliceNick

import logging


@conduit.module_loader.add_command("users")
def user_list(data, server):
    logging.debug(f'user_list called.')
    users = Connector.session.query(Users).filter(Users.online == 1).filter(Users.channel == data[1]).all()
    logging.debug(f'user_list users query called.')
    user_list = ""
    for user in users:
        logging.debug(f'user_list loop called, found ' + user.nick)
        if server.get_server(user.server):
            userNick = spliceNick(user.nick)
            userServer = server.get_server(user.server)["name"]
            if "Discord[m]" in userNick: # matrix-appservice-discord with nickPattern configured to ":nick (Discord)" # TODO: Turn this into a configuration option.
                userNick = userNick.replace("Discord[m]", "")
                userServer = "Discord"
            if "[m]" in userNick: # matrix-appservice-irc with [m] as the prefix # TODO: Turn this into a configuration option.
                userNick = userNick.replace("[m]", "")
                userServer = "Matrix"
            user_list += spliceNick(user.nick) + " (" + userServer + ") "
    server.msg(data[1], "Online Users: " + user_list)
    logging.debug(f'user_list result ' + user_list)