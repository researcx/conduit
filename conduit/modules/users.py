import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users

from conduit.functions import spliceNick

import logging


@conduit.module_loader.add_command("users")
def user_list(data, server):
    logging.debug(f'user_list called.')
    users = Connector.session.query(Users).filter(Users.online == 1).all()
    logging.debug(f'user_list users query called.')
    userList = ""
    for user in users:
        logging.debug(f'user_list loop called, found ' + user.nick)
        userList = userList + " " + spliceNick(user.nick) + " (" + server.get_server(user.server)["name"] + ")"
    server.msg(data[1], "Online Users:" + userList)
    logging.debug(f'user_list result ' + userList)