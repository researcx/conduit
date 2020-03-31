import conduit
class Invites(conduit.db.connect.declarative_base()):
    __tablename__ = 'invites'
 
    id = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer, primary_key=True)
    hostmask = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.String(length=50))
    rank = conduit.db.connect.sqlalchemy.Column(conduit.db.connect.sqlalchemy.Integer)

    def __repr__(self):
        return "<Invites(hostmask='{0}', rank='{1}')>".format(
                            self.hostmask, self.rank)