import conduit.module_loader

import conduit.db.connect as Connector
from conduit.db.users import Users

from conduit.functions import spliceNick, re_user

import logging, re

@conduit.module_loader.add_command("invite")
def invite_user(data, server):
    logging.debug(f'invite_user called.')
    msg = data[2].split(" ")
    rank = 1
    rank_name = "user"
    if ((msg[2] == "halfop") or (int(msg[2]) == 10)):
        rank = 10
        rank_name = "halfop"
    elif ((msg[2] == "op") or (int(msg[2]) == 100)):
        rank = 100
        rank_name = "op"
    userRegex = re.findall(re_user,  msg[1])
    add_user = server.add_user(userRegex[0][0], userRegex[0][1], userRegex[0][2], data[1], rank, 0)
    if add_user:
        server.describe(data[1], "invited " +msg[1] + " ("+ rank_name +")")
    else:
        server.say(data[1], msg[1] + " is already in the database")
    
@conduit.module_loader.add_command("join")
def join_ask(data, server):
    logging.debug(f'join_ask called.')
    msg = data[2].split(" ")
    nick = data[0].split('!')[0]
    userRegex = re.findall(re_user,  data[0])
    user_rank = server.check_rank(nick, userRegex[0][1], userRegex[0][2], msg[1], 1)
    print(user_rank)
    if user_rank:
        logging.debug(f"is sufficient rank ("+ str(user_rank) +"), INVITE " + nick + " " + msg[1])
        server.sendLine("INVITE " + nick + " " + msg[1])