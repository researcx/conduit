import conduit
class Servers(conduit.db.connect.declarative_base()):
    __tablename__ = 'servers'
 
    id = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer, primary_key=True)
    name = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))
    address = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))
    port = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)
    secure = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)
    nick = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))
    channel = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))
    owner = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=255))

    def __repr__(self):
        return "<Server(id='{0}', name='{1}', address='{2}', port='{3}', secure='{4}', nick='{5}', channel='{6}', owner='{7}')>".format(
                            self.id, self.name, self.address, self.port, self.secure, self.nick, self.channel, self.owner)