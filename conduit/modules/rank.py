import conduit.module_loader
import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.functions import spliceNick, re_user
import logging, re

@conduit.module_loader.add_command("rank")
def rank_user(data, server):
    logging.debug(f'rank_user called.')
    msg = data[2].split(" ")
    rank = 1
    rank_name = "user"
    rank_mode = ""
    if ((msg[2] == "halfop") or (int(msg[2]) == 10)):
        rank = 10
        rank_name = "halfop"
        rank_mode = "h"
    elif ((msg[2] == "op") or (int(msg[2]) == 100)):
        rank = 100
        rank_name = "op"
        rank_mode = "o"
    userRegex = re.findall(re_user,  msg[1])
    set_rank = server.change_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], rank, 1)
    if set_rank:
        server.say(data[1], msg[1] + " is now " + rank_name)
    else:
        server.say(data[1], msg[1] + " is already " + rank_name)
    server.check_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1])

@conduit.module_loader.add_command("disable")
def disable_user(data, server):
    logging.debug(f'disable_user called.')
    msg = data[2].split(" ")
    userRegex = re.findall(re_user,  msg[1])
    set_rank = server.change_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], 0)
    if set_rank:
        server.say(data[1], msg[1] + " is now disabled")
    else:
        server.say(data[1], msg[1] + " is already disabled")
    server.check_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], 1)

@conduit.module_loader.add_command("enable")
def enable_user(data, server):
    logging.debug(f'enable_user called.')
    msg = data[2].split(" ")
    userRegex = re.findall(re_user,  msg[1])
    set_rank = server.change_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], 1)
    if set_rank:
        server.say(data[1], msg[1] + " is now enabled")
    else:
        server.say(data[1], msg[1] + " is already enabled")
    server.check_rank(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], 0)