from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Train(Base):
    __tablename__ = 'trains'
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    departure = Column(Time)
    start_point = Column(String)
    end_point = Column(String)

    tickets = relationship('Ticket', backref='train')

    def __init__(self, name, departure, start, end):
         self.name = name
         self.departure = departure
         self.start_point = start
         self.end_point = end

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.name, self.departure)


class Ticket(Base):
    __tablename__ = 'tickets'
    electronic_id = Column(Integer, primary_key=True)

    train_id = Column(Integer, ForeignKey('trains.id'))
    cost = Column(Float)

    def __init__(self, train, electronic_id, cost):
        self.electronic_id = electronic_id
        self.cost = cost
        train.tickets.append(self)