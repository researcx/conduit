import conduit
class Users(conduit.db.connect.declarative_base()):
    __tablename__ = 'users'
 
    id = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer, primary_key=True)
    server = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)
    channel = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)
    nick = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=50))
    user = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=50))
    host = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Text)
    rank = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)
    online = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)

    def __repr__(self):
        return "<User(server='{0}', channel={1}, nick='{2}', user='{3}', host={4}, rank={5}, online={6})>".format(
                            self.server, self.channel, self.nick, self.user, self.host, self.rank, self.online)