# !/usr/bin/env python
# coding=utf-8

import os
import sys
sys.path.append('../../../')
import time
import json
import redis
import datetime

from dao_quote.quote import quote_save
from dao_quote.util.quote_fetch import quote_fetch


def init():
    global bars_list
    global bars_period_dict
    period_list = ['3min', '15min', '30min', '1hour']
    bars_list = []
    bars_period_dict = {}
    for period in period_list:
        if ('min' in period):
            bars = int(period.split('min')[0])
        elif ('hour' in period):
            bars = int(period.split('hour')[0]) * 60
        bars_list.append(bars)
        bars_period_dict[bars] = period


init()


def combine_lines_2(klines, bars):
    new_klines = []
    if (len(klines) % bars == 0):
        length = int(len(klines)/bars)
    elif (len(klines) % bars > 0):
        length = int(len(klines)/bars) + 1
    for i in range(0, length):
        klines_part = klines[i*bars:(i+1)*bars]
        klines_part_0 = klines_part[0]
        timestamp = klines_part_0[0]
        open = klines_part_0[1]
        high = klines_part_0[2]
        low = klines_part_0[3]
        close = klines_part[-1][4]
        volume = 0
        for kline in klines_part:
            high = max(high, kline[2])
            low = min(low, kline[2])
            volume += kline[5]
        new_klines.append([timestamp, open, high, low, close, volume])
    return new_klines


def quote_listen():
    channel = 'quote'
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            event_exchange = event_dict['exchange']
            event_symbol = event_dict['symbol']
            event_type = event_dict['event_type']
            data = json.loads(event_dict['data'])
            if event_type == 'kline':
                process_event_kline(r, channel, event_dict, event_exchange, event_symbol, event_type, data)
            else:
               pass


def process_event_kline(r, channel, event_dict, event_exchange, event_symbol, event_type, data):
    global bars_list
    global bars_period_dict

    for bars in bars_list:
        if (float(data[-1][0])/1000 % (60 * bars) == 0):
            period = bars_period_dict[bars]
            event_type_ = '{}.{}'.format(event_type, period)
            key_name = '{}_{}_{}'.format(event_exchange,
                       event_symbol, event_type_)
            event_dict['event_type'] = event_type_

            # length = len(data) - 1
            length = 499
            klines = data[-bars*(int(length/bars)-1)-1:-1]
            klines = combine_lines_2(klines, bars)
            klines.append(data[-1])
            data_ = klines

            db_name = 'dao_quote.db'
            quote_save.save_kline(db_name, key_name, data_)
            data_ = json.dumps(data_)
            event_dict['data'] = data_
            r.publish(channel, json.dumps(event_dict))
            del klines
            del data_


def main():
    quote_listen()


if __name__ == '__main__':
    main()
