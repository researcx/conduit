import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users

from conduit.functions import spliceNick, re_user

import logging, re

@conduit.module_loader.add_command("disable")
def disable_user(data, server):
    logging.debug(f'disable_user called.')
    msg = data[2].split(" ")
    userRegex = re.findall(re_user,  msg[1])
    setRank = server.change_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], 0)
    if setRank:
        server.say(data[1], msg[1] + " is now disabled")
    else:
        server.say(data[1], msg[1] + " is already disabled")
    server.check_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1])