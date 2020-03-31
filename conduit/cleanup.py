#!/usr/bin/env python3
import conduit.db.connect as Connector
from conduit.db.users import Users
from conduit.db.servers import Servers
from conduit.db.messages import Messages
from conduit.functions import RepeatTimer
import sys

instances = [int(i) for i in sys.argv[1].split(";") if i] 
def checkMessages():
    messages = Connector.session.query(Messages).all()
    for message in messages:
        sent = [int(i) for i in message.sent.split(";") if i] 
        if set(sent) == set(instances):
            Connector.session.delete(message)
            Connector.session.commit()

if __name__ == "__main__":
    checkMessages()
    # timer = RepeatTimer(1.5, checkMessages)
    # timer.start()