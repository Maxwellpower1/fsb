# !/usr/bin/env python
# coding=utf-8

import time
import json
import redis
import datetime
import pathmagic

from multiprocessing import Process
from dao_quote.bar_generator import combine_bar
# from dao_quote.util.quote_fetch import quote_fetch


def test_quote_listen():
    combine_bar.quote_listen()


def test_listen_redis():
    channel = 'quote'
    key_name = 'okexf_eos_usd-quarter_kline.3min'
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    p.subscribe(key_name)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            event_type = event_dict['event_type']
            event_exchange = event_dict['exchange']
            event_symbol = event_dict['symbol']
            data = json.loads(event_dict['data'])
            if event_type == 'ticker':
                # on_tick(event_dict)
                # print(event_dict)
                # try:
                #     print(event_dict['key_name'], data['last'])
                #     print('*' * 50)
                # except Exception as e:
                #     pass
                pass
            elif event_type in ['kline.1hour', 'kline.3min', 'kline.15min', 'kline']:
            # elif event_type in ['kline.1hour']:
                if (event_exchange == 'okexf' and event_symbol == 'eos_usd-quarter'):
                    # print(datetime.datetime.now(), data[-1])
                    timestamp = data[-1][0]/1000
                    time_now = shift_time(timestamp)
                    print(datetime.datetime.now(), time_now, event_type, event_exchange, event_symbol)
                    print(data[-1])
                    print('*' * 50)
                # try:
                #     print(event_dict['key_name'], data[-1])
                #     print('*' * 50)
                # except Exception as e:
                #     pass
            elif event_type == 'depth':
                # print(event_dict)
                # if (event_exchange == 'okexf' and event_symbol == 'eos_usd-quarter'):
                #     data = json.loads(event_dict['data'])
                #     print(datetime.datetime.now(), time.time(), data['ts'], data)
                # try:
                #     print(event_dict['key_name'], data['asks'][0])
                #     print('*' * 50)
                # except Exception as e:
                #     pass
                pass


def shift_time(timestamp):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(timestamp)
    return time.strftime(format, value)


def test_multi():
    p1 = Process(target=test_quote_listen, args=())
    p1.start()
    p2 = Process(target=test_listen_redis, args=())
    p2.start()


def main():
    # test_quote_listen()
    # test_multi()
    test_listen_redis()


if __name__ == '__main__':
    main()
