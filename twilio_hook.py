#coding: utf-8

from flask import Flask, request, redirect
import twilio.twiml
import datetime
from entites import Ticket, Train


app = Flask(__name__)
cfg = Config('grazed.conf')
STORE_DBURI = cfg.get_value('store', 'dburi')
engine = create_engine(STORE_DBURI or 'sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)


@app.route("/sms_request", methods=['GET', 'POST'])
def reply_to_sms():
    body = request.values.get('Body', '')
    resp = twilio.twiml.Response()

    if body == 'hello':
        resp.sms(u'Hello, world!')
    return unicode(resp)

if __name__ == '__main__':
    app.run(debug=True)