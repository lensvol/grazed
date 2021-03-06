# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
import json
from decimal import Decimal
import requests
import time
from optparse import OptionParser

RZD_LOGIN_CHECK_URL = u'https://rzd.ru/timetable/j_security_check'
RZD_ENDPOINT_URL = u'https://pass.rzd.ru/ticket/secure/ru'
RZD_LOGOUT_URL = 'http://rzd.ru/main/ibm_security_logout?logoutExitPage=http://rzd.ru'


def json_default(o):
    r'''
    Обработка особых случаев кодирования данных в JSON.

    @param  o   Кодируемый объект
    @type   o   object
    '''
    if isinstance(o, datetime.date):
        # JSON-кодировщик не понимает даты с годами меньше 1900 :-(
        # Обычно это связано с datetime.date.min
        if o.year < 1900:
            date = datetime.datetime(1900, o.month, o.day, 0, 0, 0, 0)
        else:
            date = o
        return date.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif isinstance(o, Decimal):
        return unicode(o)
    return json.JSONEncoder.default(o)


def rzd_post(session, url, data=None, wait_seconds=2):
    resp = session.post(url, data=data)
    resp_data = json.loads(resp.text)

    if 'RID' in resp_data:
        time.sleep(wait_seconds)
        request_data = dict(data)
        request_data['rid'] = resp_data['RID']
        return rzd_post(session, url, data=request_data, wait_seconds=wait_seconds)
    return resp_data


def load_rzd_orders(login, password):
    u'''
    Загрузка списка заказов билетов через сайт РЖД. При необходимости
     выполняет загрузку списка по частям, если за один запрос получить
     весь список не получилось (не совсем понятно, чем они руководствуются).

    Из соображений вежливости, между каждым запросом проходит по 3 секунды.

    @param  login   Имя пользователя на сайте rzd.ru.
    @type   login   unicode

    @param  password   Пароль на сайте rzd.ru.
    @type   password   unicode
    '''

    session = requests.Session()

    login_data = {
        'j_username': login,
        'j_password': password,
        'action': u'Вход'
    }
    tickets_data = {
        'STRUCTURE_ID': 5235,
        'layer_id': 5419,
        'page': 1,
        'date0': '',
        'date1': '',
        'number': ''
    }
    result = {
        'totalCount': 0,
        'slots': []
    }

    # Получаем куки для входа в систему
    resp = session.get(RZD_LOGIN_CHECK_URL)
    # Входим в систему
    resp = session.post(RZD_LOGIN_CHECK_URL, data=login_data)

    # Получаем список билетов
    data = rzd_post(session, RZD_ENDPOINT_URL, data=tickets_data)
    result.update(data)
    result['totalCount'] = len(data['slots'])

    # Выйдем из системы
    session.post(RZD_LOGOUT_URL)
    return result


def extract_tickets_data(orders, active_only=False):
    u'''
    Извлечение и преобразование данных о билетах из списка заказов с сайта РЖД.
    Необходимость в этом существует, так как в рамках одного заказа может находиться
    несколько билетов на разных людей, каждый со своим номером.

    @param  orders  Список заказов, полученных из AJAX-запроса к сервису РЖД.
    @type   orders  list of dict
    '''
    tickets = []

    for order_container in orders:
        order = order_container['lst'][0]
        departure = datetime.datetime.strptime('%s %s' % (order['date0'], order['time0']),
                                               '%d.%m.%Y %H:%M')

        for personal_ticket in order['lst']:
            if active_only and order['inactive']:
                continue

            ticket = {
                'departure': departure,
                'from_station': order['station0'],
                'to_station': order['station1'],
                # Номер поезда (см. http://www.rzd.me/inform-block/train-numerate/)
                'train': order['train'],
                'cost': personal_ticket['cost'],
                'place': personal_ticket['place'],
                'fio': personal_ticket['name'],
                # Вагон
                'car': order['car'],
                # Класс вагона
                # (см. http://pass.rzd.ru/timetable/public/ru?STRUCTURE_ID=735&layer_id=5499)
                'car_class': order['carCls'],
                # У каждого _билета_ есть свой номер для распечатки в терминале,
                # однако id у заказа указывает на билет его создателя.
                # Судя по выгрузке, 'number' у отдельных билетов начал проставляться
                # примерно с июля 2012 года.
                'electronic_id': personal_ticket['number'] or order['id'],
                'order_id': order['id']
            }
            tickets.append(ticket)

    return tickets


def main():
    parser = OptionParser(usage='Usage: %prog [options] [username] [password]')
    parser.add_option('', '--active', dest='active_only', action='store_true',
                      help=u'Display tickets from active orders only.')
    parser.add_option('', '--json-dump', dest='json_dump', action='store_true',
                      help=u'Dump tickets data in JSON.')
    (options, args) = parser.parse_args()

    if len(args) == 2:
        rzd_login, rzd_pass = args
    else:
        parser.print_help()
        exit(-1)

    if not rzd_login or not rzd_pass:
        print 'ERROR: Authenthication data has not been specified!'
    else:
        orders = load_rzd_orders(rzd_login, rzd_pass)
        tickets = extract_tickets_data(orders['slots'], active_only=options.active_only)

        if options.json_dump:
            print json.dumps(tickets, indent=4, default=json_default)
        else:
            for ticket in tickets:
                print u'%(electronic_id)s, %(departure)s, %(train)s поезд, ' \
                      u'%(car)s вагон, %(place)s место' % ticket


if __name__ == '__main__':
    main()
