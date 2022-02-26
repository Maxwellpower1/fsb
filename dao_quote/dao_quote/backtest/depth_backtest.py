#!/usr/bin/env python
# coding=utf-8

import sys
import json
import time
import redis

sys.path.append('../../../strategy_research')
from strategy_research.data import depth
from strategy_research.data import tick


def main_test():
    global r
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)

    exchange_1 = 'okexf'
    # exchange_1 = 'okex'
    # exchange_1 = 'huobif'
    symbol_1 = 'btc_usd-quarter'
    # symbol_1 = 'eos_usd-quarter'
    # symbol_1 = 'eos_usdt'

    # exchange_2 = 'huobi'
    exchange_2 = 'okex'
    # exchange_2 = 'huobif'
    # symbol_2 = 'btc_usdt'
    symbol_2 = 'okb_usdt'
    # symbol_2 = 'eosusdt'

    begin_time = '2019-09-25 19:00:00'
    end_time = '2019-09-27 23:59:00'

    depths_1 = depth.get_sqlite_depths(exchange_1, symbol_1, begin_time, end_time)
    ticks_1 = tick.get_sqlite_ticks(exchange_1, symbol_1, begin_time, end_time)

    depths_2 = depth.get_sqlite_depths(exchange_2, symbol_2, begin_time, end_time)
    ticks_2 = tick.get_sqlite_ticks(exchange_2, symbol_2, begin_time, end_time)

    quote_all_dict = {}
    for depth_dict in depths_1:
        depth_dict['exchange'] = exchange_1
        depth_dict['symbol'] = symbol_1
        quote_all_dict[depth_dict['ts']] = depth_dict
    for tick_dict in ticks_1:
        tick_dict['exchange'] = exchange_1
        tick_dict['symbol'] = symbol_1
        quote_all_dict[tick_dict['ts']] = tick_dict
    for depth_dict in depths_2:
        depth_dict['exchange'] = exchange_2
        depth_dict['symbol'] = symbol_2
        quote_all_dict[depth_dict['ts']] = depth_dict
    for tick_dict in ticks_2:
        tick_dict['exchange'] = exchange_2
        tick_dict['symbol'] = symbol_2
        quote_all_dict[tick_dict['ts']] = tick_dict
    for timestamp in sorted(quote_all_dict.keys()):
        depth_dict = quote_all_dict.get(timestamp, None)
        tick_dict = quote_all_dict.get(timestamp, None)
        if ((depth_dict is not None) and ('asks' in depth_dict)):
            exchange = depth_dict['exchange']
            symbol = depth_dict['symbol']
            del depth_dict['exchange']
            del depth_dict['symbol']
            key_name = '{}_{}_depth'.format(exchange, symbol)
            data = depth_dict
            send_event(key_name, data)
        if ((tick_dict is not None) and ('ask' in tick_dict)):
            exchange = tick_dict['exchange']
            symbol = tick_dict['symbol']
            del tick_dict['exchange']
            del tick_dict['symbol']
            key_name = '{}_{}_ticker'.format(exchange, symbol)
            data = tick_dict
            send_event(key_name, data)


def send_event(key_name, data):
    global r
    channel = 'quote'
    params = key_name.split('_')
    exchange = params[0]
    event_type = params[-1]
    if (len(params) == 4):
        symbol = '{}_{}'.format(params[1], params[2])
    elif (len(params) == 5):
        symbol = '{}_{}_{}'.format(params[1], params[2], params[3])
    else:
        symbol = params[1]
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    r.publish(channel, json.dumps(event_dict))
    return True


def main():
    main_test()


if __name__ == '__main__':
    main()
