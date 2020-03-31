import conduit
class Messages(conduit.db.connect.declarative_base()):
    __tablename__ = 'messages'
 
    id = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer, primary_key=True)
    server = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)
    sent = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))
    channel = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)
    sender = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)
    message = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)
    type = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)

    def __repr__(self):
        return "<Message(id='{0}', server='{1}', sent='{2}', channel='{3}', sender='{4}', message='{5}', type='{6}')>".format(
                            self.id, self.server, self.sent, self.channel, self.sender, self.message, self.type)