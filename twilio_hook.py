#coding: utf-8

import datetime
import twilio.twiml

from flask import Flask, request, redirect
from entities import Ticket, Train

from store import get_store_session
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
session = get_store_session()

@app.route("/sms_request", methods=['GET', 'POST'])
def reply_to_sms():
    body = request.values.get('Body', '')
    resp = twilio.twiml.Response()

    if 'next' in body.lower():
        # Отсылаем информацию по всем билетам        
        try:
            tickets = session.query(Ticket)\
                             .filter(Ticket.departure >= datetime.datetime.now())\
                             .order_by(Ticket.departure)
            lines = []
            for t in tickets:
                resp.sms(u'%s, %s,%i вагон,%i место' % (
                    t.departure.strftime('%d.%m.%Y %H:%M'),                    
                    t.train.name,
                    t.car,
                    t.seat
                ))
            
            result = '\n'.join(lines)
        except NoResultFound:
            result = u'Nothing to see here, move along.'
    return unicode(resp).encode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)