#coding: utf-8

import datetime
import json
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from config import Config
from entities import Train, Ticket, Base

cfg = Config('grazed.conf')

def get_store_session(): 
    STORE_DBURI = cfg.get_value('store', 'dburi')
    # Пробуем создать сессию для работы с БД
    engine = create_engine(STORE_DBURI or 'sqlite:///:memory:', echo=False)
    Session = sessionmaker(bind=engine)

    # Заполняем БД согласно схеме
    Base.metadata.create_all(engine)
    return Session()

if __name__ == '__main__':
    session = get_store_session()
    # Количество билетов, добавленных в эту загрузку
    new_tickets = 0

    with open(sys.argv[1], 'r') as tickets_dump:
        tickets = json.loads(tickets_dump.read())
        for ticket in tickets:            
            departure = datetime.datetime.strptime(ticket['departure'], '%Y-%m-%d %H:%M:%S.%f')
            
            # Проверяем, есть ли данные по такому поезду в базе. Если нет - создадим.
            # TODO: схлопывать поезда по численной части номера, без учета буквенного кода.
            try:
                train = session.query(Train).\
                               filter(Train.name == ticket['train']).\
                               filter(Train.start_point == ticket['from_station']).\
                               filter(Train.end_point == ticket['to_station']).one()
            except NoResultFound:
                train = Train(ticket['train'], ticket['from_station'], ticket['to_station'])
                session.add(train)

            # Проверяем, есть ли данные по такому электронному билету.
            try:
                ticket = session.query(Ticket)\
                                .filter(Ticket.electronic_id == ticket['electronic_id']).one()
            except NoResultFound:
                stored_ticket = Ticket(train)
                stored_ticket.electronic_id = ticket['electronic_id']
                stored_ticket.departure = departure
                stored_ticket.car = int(ticket['car'])
                stored_ticket.seat = int(ticket['place']) if ticket['place'] else 0
                session.add(stored_ticket)
                new_tickets += 1

        session.commit()

        print 'Total: %i tickets for %i trains (%i new)' % (session.query(Ticket).count(),
                                                   session.query(Train).count(), new_tickets)
