import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
engine = sqlalchemy.create_engine('mysql+pymysql://conduit:conduit@localhost/conduit', echo=False, isolation_level="READ UNCOMMITTED")

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()