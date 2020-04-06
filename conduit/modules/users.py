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
            user_list += spliceNick(user.nick) + " (" + server.get_server(user.server)["name"] + ") "
    server.msg(data[1], "Online Users: " + user_list)
    logging.debug(f'user_list result ' + user_list)