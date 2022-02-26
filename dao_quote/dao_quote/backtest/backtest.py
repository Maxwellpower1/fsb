#!/usr/bin/env python
# coding=utf-8

import sys
import json
import time
import redis

sys.path.append('../../')
import pathmagic
from dao_quote.util.convert import convert
from dao_quote.util.quote_fetch import quote_fetch


def main_test():
    global r
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)

    # exchange_1 = 'okexf'
    # exchange_1 = 'ctp'
    exchange_1 = 'huobif'
    symbol_1 = 'btc_usd-quarter'
    # symbol_1 = 'eos_usd-quarter'
    # symbol_1 = 'xrp_usd-quarter'
    # symbol_1 = 'eth_usd-quarter'
    # symbol_1 = 'ltc_usd-quarter'
    # symbol_1 = 'c2009'

    # exchange_2 = 'okex'
    exchange_2 = 'huobi'
    # exchange_2 = 'okexf'
    # exchange_2 = 'huobif'
    symbol_2 = 'btc_usdt'
    # symbol_2 = 'eos_usdt'
    # symbol_2 = 'btc_usd-quarter'
    # symbol_2 = 'eos_usd-this_week'
    timer_type = 3
    timer_key_name = 'dao_timer_{}s'.format(timer_type)

    begin_time = '2020-02-15 00:00:00'
    end_time = '2020-04-01 00:00:00'
    period = '1min'
    begin_timestamp = convert.to_timestamp(begin_time)
    end_timestamp = convert.to_timestamp(end_time)

    # klines_1 = kline.get_sqlite_klines(exchange_1, symbol_1, begin_time, end_time)
    klines_1 = quote_fetch.get_backtest_kline_db(exchange_1, symbol_1, period, begin_timestamp, end_timestamp)
    # klines_2 = kline.get_sqlite_klines(exchange_2, symbol_2, begin_time, end_time)
    klines_2 = quote_fetch.get_backtest_kline_db(exchange_2, symbol_2, period, begin_timestamp, end_timestamp)

    # klines_1 = change_timestamp(klines_1)
    # klines_2 = change_timestamp(klines_2)

    for i in range(13, len(klines_1)):
        bars_1 = klines_1[i-12:i]
        bars_2 = klines_2[i-12:i]

        # on_bar()
        data = bars_1
        key_name = '{}_{}_kline'.format(exchange_1, symbol_1)
        send_event(key_name, data)

        # on_bar()
        data = bars_2
        key_name = '{}_{}_kline'.format(exchange_2, symbol_2)
        send_event(key_name, data)

        # on_timer()
        data = {}
        timestamp = float(bars_1[-1][0])
        data['ts'] = timestamp
        data['time_now'] = convert.shift_time(timestamp)
        send_event(timer_key_name, data)


def send_event(key_name, data):
    global r
    params = key_name.split('_')
    exchange = params[0]
    if ('timer' in key_name):
        event_type = 'timer'
    else:
        event_type = params[-1]
    if (len(params) == 4):
        symbol = '{}_{}'.format(params[1], params[2])
    elif (len(params) == 5):
        symbol = '{}_{}_{}'.format(params[1], params[2], params[3])
    else:
        symbol = params[1]
    event_dict = {}
    event_dict['key_name'] = key_name
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    event_dict = json.dumps(event_dict)
    r.publish(key_name, event_dict)
    return True


def change_timestamp(klines):
    klines = [[i[0]*1000, i[1], i[2], i[3], i[4], i[5]] for i in klines]
    return klines


def main():
    main_test()


if __name__ == '__main__':
    main()
