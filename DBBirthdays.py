from sqlalchemy import Column, Integer, String, Date
from config import Base
import birthday_class


class DBBirthdays(Base):
    __tablename__ = 'Birthdays'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    date = Column(Date)
    name = Column(String)
    link = Column(String)

    def __init__(self, user, date, name, link=None):
        self.user = user
        self.date = date
        self.name = name
        self.link = link

    def __repr__(self):
        return "<b>" + str(self.date.day) + " " + \
               birthday_class.NumberToMonth[self.date.month] + "</b>" + "\n" + self.name

    def message(self):
        return "<b>" + str(self.date.day) + " " + \
               birthday_class.NumberToMonth[self.date.month] + "</b>" + "\n" + self.name
