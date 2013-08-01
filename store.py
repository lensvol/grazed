#coding: utf-8

import json
import sys

from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)


class Train(Base):
    __tablename__ = 'trains'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    departure = Column(Time)
    travels = relationship('Travel', backref='train')

class Travel(Base):
    __tablename__ = 'travels'
    id = Column(Integer, primary_key=True)
    start_point = Column(String)
    end_point = Column(String)
    train_id = Column(Integer, ForeignKey('trains.id'))

    def __init__(self, start, end, train):
        pass

class Ticket(Base):
    __tablename__ = 'tickets'
    electronic_id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('travels.id'))
    cost = Column(Float)

Base.metadata.create_all(engine)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as tickets_dump:
        tickets = json.loads(tickets_dump.read())

