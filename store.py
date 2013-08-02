#coding: utf-8

import datetime
import json
import sys

from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)


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


Base.metadata.create_all(engine)

if __name__ == '__main__':
    session = Session()

    with open(sys.argv[1], 'r') as tickets_dump:
        tickets = json.loads(tickets_dump.read())
        for ticket in tickets:            
            departure = datetime.datetime.strptime(ticket['departure'], '%Y-%m-%d %H:%M:%S.%f')
            
            try:
                train = session.query(Train).\
                               filter(Train.name == ticket['train']).\
                               filter(Train.departure == departure.time()).\
                               filter(Train.start_point == ticket['from_station']).\
                               filter(Train.end_point == ticket['to_station']).one()
            except NoResultFound:
                train = Train(ticket['train'], departure.time(), 
                              ticket['from_station'], ticket['to_station'])
                session.add(train)

            try:
                ticket = session.query(Ticket)\
                                .filter(Ticket.electronic_id == ticket['electronic_id']).one()
            except NoResultFound:
                ticket = Ticket(train, ticket['electronic_id'], ticket['cost'])
                session.add(ticket)

        session.commit()

        print 'Total: %i tickets for %i trains' % (session.query(Ticket).count(),
                                                   session.query(Train).count())
