#!/usr/bin/env python3
import subprocess
import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages

servers = Connector.session.query(Servers).all()
server_id = ""
for server in servers:
    server_id = server_id + str(server.id) + ";"
    subprocess.Popen(["python", "ircbot.py", str(server.id), server.address, str(server.port), server.nick, server.channel, server.owner, str(server.secure)])
subprocess.Popen(["python", "cleanup.py", server_id])