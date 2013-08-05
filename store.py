#coding: utf-8

import datetime
import json
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from entities import Train, Ticket, Base

engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)

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
