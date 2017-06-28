from sqlalchemy import Column, Integer, String, DateTime
from config import engine, Base, db_session


class DBMessages(Base):
    __tablename__ = 'Messages'
    id = Column(Integer, primary_key=True)
    user = Column(String, unique=True)
    name = Column(String)
    link = Column(String)
    month = Column(String)
    day = Column(String)

    def __init__(self, user, name=None, link=None, month=None, day=None):
        self.user = user
        self.name = name
        self.link = link
        self.month = month
        self.day = day
