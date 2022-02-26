#!/usr/bin/env python
# coding=utf-8

import redis
import json
import traceback
import pathmagic
from multiprocessing import Process

from dao_quote.settings import config_collect


def test_brpop():
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    # exchange = 'okex'
    # exchange = 'okexf'
    # exchange = 'huobi'
    # exchange = 'huobif'
    exchange = 'binance'
    # exchange = 'fcoin'

    # type = 'ticker'
    # type = 'trade'
    # type = 'depth'
    type = 'depthall'
    while True:
        try:
            value = r.brpop(config_collect.LPUSH_RECORD_MQ)
            value = value[1].decode('utf-8')
            event_dict = json.loads(value)
            if (event_dict['exchange'] == exchange):
                if (event_dict['event_type'] == type):
                    print(event_dict['key_name'])
        except Exception as e:
            exception_msg = traceback.format_exc()
            print('record err: {}'.format(exception_msg))


def test_collect_wss_one(exchange, symbol, type_list):
    symbol_list = [symbol]
    if (exchange == 'okexf'):
        from dao_quote.util.exchange_api.okexf import wss_okexf
        wss_okexf.main(symbol_list, type_list)
    elif (exchange == 'okex'):
        from dao_quote.util.exchange_api.okex import wss_okex
        wss_okex.main(symbol_list, type_list)
    elif (exchange == 'huobi'):
        from dao_quote.util.exchange_api.huobi import wss_huobi
        wss_huobi.main(symbol_list, type_list)
    elif (exchange == 'huobif'):
        from dao_quote.util.exchange_api.huobif import wss_huobif
        wss_huobif.main(symbol_list, type_list)
    elif (exchange == 'binance'):
        from dao_quote.util.exchange_api.binance import wss_binance
        wss_binance.main(symbol_list, type_list)
    elif (exchange == 'fcoin'):
        from dao_quote.util.exchange_api.fcoin import wss_fcoin
        wss_fcoin.main(symbol_list, type_list)


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


def test_collect_wss():
    # exchange = 'okex'
    # exchange = 'huobi'
    # exchange = 'binance'
    exchange = 'fcoin'
    symbol = 'btc_usdt'
    # exchange = 'okexf'
    # exchange = 'huobif'
    # symbol = 'btc_usd-quarter'

    type_list = ['ticker', 'depth', 'trade', 'depthall']
    p1 = Process(target=test_collect_wss_one, args=(exchange, symbol, type_list, ))
    p2 = Process(target=test_listen_key_name, args=())
    p1.start()
    p2.start()
    print('running...')


def main():
    # test_brpop()
    test_collect_wss()


if __name__ == '__main__':
    main()
