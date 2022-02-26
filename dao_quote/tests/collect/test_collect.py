# !/usr/bin/env python
# coding=utf-8

import time
import json
import redis
import datetime
import pathmagic
from multiprocessing import Process

from dao_quote.settings import config_collect
from dao_quote.util.convert import convert


def test_listen_redis():
    channel = config_collect.CHANNEL
    redis_host = config_collect.REDIS_HOST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            key_name = event_dict['key_name']
            event_type = event_dict['event_type']
            event_exchange = event_dict['exchange']
            event_symbol = event_dict['symbol']
            data = json.loads(event_dict['data'])
            if event_type == 'ticker':
                try:
                    print(key_name, data['last'])
                    print('*' * 50)
                except Exception as e:
                    print(key_name, e)
            elif event_type in ['kline.1hour', 'kline.3min', 'kline.15min', 'kline']:
                try:
                    print(key_name, data[-1])
                    print('*' * 50)
                except Exception as e:
                    print(key_name, e)
            elif event_type == 'depth':
                try:
                    print(key_name, data['asks'][0])
                    print('*' * 50)
                except Exception as e:
                    print(key_name, e)


def test_set_one_type_symbol(exchange, symbol, type_list):
    global pool
    print('getting...')
    from dao_quote.collect import collect
    redis_host = config_collect.REDIS_HOST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    collect.set_pool(pool)
    for type_ in type_list:
        collect.set_one_type_symbol(exchange, symbol, type_)


def test_listen_key_name():
    print('listening...')
    channel = config_collect.CHANNEL
    redis_host = config_collect.REDIS_HOST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            key_name = event_dict['key_name']
            event_type = event_dict['event_type']
            event_exchange = event_dict['exchange']
            event_symbol = event_dict['symbol']
            data = json.loads(event_dict['data'])
            print(key_name)
            print(data)


def test_listen_by_key_name(key_name_):
    print('listening...')
    channel = config_collect.CHANNEL
    redis_host = config_collect.REDIS_HOST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            key_name = event_dict['key_name']
            if (key_name == key_name_):
                event_type = event_dict['event_type']
                event_exchange = event_dict['exchange']
                event_symbol = event_dict['symbol']
                data = json.loads(event_dict['data'])
                print(datetime.datetime.now(), data[-1])


def test_collect():
    exchange = 'okex'
    # exchange = 'huobi'
    # exchange = 'binance'
    symbol = 'btc_usdt'
    # exchange = 'okexf'
    # exchange = 'huobif'
    # symbol = 'btc_usd-quarter'

    type_list = ['ticker', 'depth', 'trade']
    p1 = Process(target=test_set_one_type_symbol, args=(exchange, symbol, type_list, ))
    p2 = Process(target=test_listen_key_name, args=())
    p1.start()
    p2.start()
    print('running...')


def main():
    # test_listen_redis()
    # test_collect()
    test_listen_by_key_name('okexf_btc_usd-quarter_kline')


if __name__ == '__main__':
    main()
