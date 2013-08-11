#coding: utf-8

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Train(Base):
    u'''
    Поезд, отправляющийся из точки А до точки Б в определенное время.
    '''
    __tablename__ = 'trains'
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    start_point = Column(String)
    end_point = Column(String)

    tickets = relationship('Ticket', backref='train')

    def __init__(self, name, start, end):
         self.name = name
         self.start_point = start
         self.end_point = end

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.name, self.departure)


class Ticket(Base):
    u'''
    Электронный билет, купленный на сайте РЖД (http://pass.rzd.ru).
    '''
    __tablename__ = 'tickets'
    electronic_id = Column(BigInteger, primary_key=True)

    departure = Column(DateTime)
    car = Column(Integer)
    seat = Column(Integer)

    train_id = Column(Integer, ForeignKey('trains.id'))
    cost = Column(Float)

    def __init__(self, train):
        train.tickets.append(self)
