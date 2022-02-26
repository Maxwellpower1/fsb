# coding=utf-8

import os
import time
import json
import redis
import asyncio
import gevent
import sqlite3

from gevent import monkey; monkey.patch_all()

from dao_quote.quote import quote_save
from dao_quote.quote import quote_set


def get_exchange_dict():
    exchange_dict = {
        'OKEX': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt', 'okb_usdt'],
        'okexf': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
                  'eth_usd-quarter', 'xrp_usd-quarter',
                  'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
                  'eth_usd-this_week', 'xrp_usd-this_week',
                  'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
                  'eth_usd-next_week', 'xrp_usd-next_week'],
        'Huobi': ['btcusdt', 'eosusdt', 'ltcusdt', 'ethusdt', 'xrpusdt'],
        'huobif': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
                   'eth_usd-quarter',
                   'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
                   'eth_usd-this_week',
                   'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
                   'eth_usd-next_week'],
        'Binance': ['BTCUSDT', 'EOSUSDT', 'LTCUSDT', 'ETHUSDT', 'XRPUSDT']
    }
    return exchange_dict


def get_db_name(timestamp):
    format = '%Y%m%d'
    value = time.localtime(timestamp)
    date = time.strftime(format, value)
    db_name = 'quote_{}.db'.format(date)
    return db_name


def combine_lines(klines, bars):
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
            low = min(low, kline[3])
            volume += kline[5]
        new_klines.append([timestamp, open, high, low, close, volume])
    return new_klines


async def async_set_one_type_symbol(db_name, exchange, symbol, type):
    global conn
    global conn_bar
    global pool
    global kline_dict
    global bars_list
    global bars_period_dict
    global bar_key_name_list

    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    key_name = key_name.lower()
    channel = 'quote'
    event_type = type
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    r = redis.StrictRedis(connection_pool=pool)

    if (type == 'ticker'):
        data = await quote_set.set_async_ticker(db_name, exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            quote_save.wss_save_tick(conn, key_name, timestamp, data)
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            r.publish(channel, json.dumps(event_dict))
        else:
            pass
    elif (type == 'kline'):
        db_name = 'dao_quote.db'
        data = await quote_set.set_async_kline(db_name, exchange, symbol)
        if (data != {}):
            r = redis.StrictRedis(connection_pool=pool)
            r[key_name] = str(data)
            kline_time = float(data[-1][0])
            try:
                if (kline_dict.get(key_name, 0) < kline_time):
                    quote_save.wss_save_bar(conn_bar, key_name, data)
                    event_dict['data'] = json.dumps(data)
                    r.publish(channel, json.dumps(event_dict))
                    kline_dict[key_name] = kline_time
                    # process multi min
                    if (key_name in bar_key_name_list):
                        for bars in bars_list:
                            if (float(data[-1][0])/1000 % (60 * bars) == 0):
                                period = bars_period_dict[bars]
                                key_name_ = '{}.{}'.format(key_name, period)
                                event_type_ = '{}.{}'.format(event_type, period)
                                event_dict['event_type'] = event_type_

                                # length = len(data) - 1
                                length = 499
                                klines = data[-bars*(int(length/bars)-1)-1:-1]
                                klines = combine_lines(klines, bars)
                                klines.append(data[-1])
                                data_ = klines

                                quote_save.wss_save_bar(conn_bar, key_name_, data_)
                                data_ = json.dumps(data_)
                                event_dict['data'] = data_
                                r.publish(channel, json.dumps(event_dict))
                                del klines
                                del data_
                            else:
                                pass
                    else:
                        pass
                elif (key_name not in kline_dict):
                    kline_dict[key_name] = kline_time
                    del data
                else:
                    del data
            except Exception as e:
                print(e)
                kline_dict[key_name] = kline_time
        else:
            pass
    elif (type == 'depth'):
        data = await quote_set.set_async_depth(db_name, exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            quote_save.wss_save_depth(conn, key_name, timestamp, data)
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            r.publish(channel, json.dumps(event_dict))
        else:
            pass
    return None


def async_update_process():
    global conn
    global conn_bar
    global pool
    global kline_dict
    global bars_list
    global bars_period_dict
    global bar_key_name_list

    kline_dict = {}

    period_list = ['3min', '15min', '1hour']
    bar_key_name_list = ['okexf_btc_usd-quarter_kline', 'huobif_btc_usd-quarter_kline']
    bars_list = []
    bars_period_dict = {}
    for period in period_list:
        if ('min' in period):
            bars = int(period.split('min')[0])
        elif ('hour' in period):
            bars = int(period.split('hour')[0]) * 60
        bars_list.append(bars)
        bars_period_dict[bars] = period

    exchange_dict = get_exchange_dict()
    type_list = ['ticker', 'kline', 'depth']
    timestamp = time.time()
    db_name = get_db_name(timestamp)
    conn = sqlite3.connect(db_name, timeout=21)
    conn_bar = sqlite3.connect('dao_quote.db', timeout=21)
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    while True:
        task_list = []
        for exchange in exchange_dict:
            symbol_list = exchange_dict[exchange]
            for symbol in symbol_list:
                for type in type_list:
                    task_list.append(async_set_one_type_symbol(db_name, exchange, symbol, type))
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(*task_list))
        loop.close()
        time.sleep(0.3)
        print(time.time())
        pass


def set_one_type_symbol(db_name, exchange, symbol, type):
    global conn
    global conn_bar
    global pool
    global kline_dict
    global bars_list
    global bars_period_dict
    global bar_key_name_list

    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    key_name = key_name.lower()
    channel = 'quote'
    event_type = type
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    r = redis.StrictRedis(connection_pool=pool)

    if (type == 'ticker'):
        data = quote_set.set_ticker(db_name, exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            quote_save.wss_save_tick(conn, key_name, timestamp, data)
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            r.publish(channel, json.dumps(event_dict))
            del event_dict
            del data
        else:
            del event_dict
            del data
    elif (type == 'kline'):
        db_name = 'dao_quote.db'
        data = quote_set.set_kline(db_name, exchange, symbol)
        if (data != {}):
            kline_time = float(data[-1][0])
            try:
                if (kline_dict.get(key_name, 0) < kline_time):
                    quote_save.wss_save_bar(conn_bar, key_name, data)
                    event_dict['data'] = json.dumps(data)
                    r.publish(channel, json.dumps(event_dict))
                    kline_dict[key_name] = kline_time
                    # process multi min
                    if (key_name in bar_key_name_list):
                        for bars in bars_list:
                            if (float(data[-1][0])/1000 % (60 * bars) == 0):
                                period = bars_period_dict[bars]
                                key_name_ = '{}.{}'.format(key_name, period)
                                event_type_ = '{}.{}'.format(event_type, period)
                                event_dict['event_type'] = event_type_

                                # length = len(data) - 1
                                length = 499
                                klines = data[-bars*(int(length/bars)-1)-1:-1]
                                klines = combine_lines(klines, bars)
                                klines.append(data[-1])
                                data_ = klines

                                quote_save.wss_save_bar(conn_bar, key_name_, data_)
                                data_ = json.dumps(data_)
                                event_dict['data'] = data_
                                r.publish(channel, json.dumps(event_dict))
                                del klines
                                del data_
                            else:
                                pass
                    else:
                        pass
                elif (key_name not in kline_dict):
                    kline_dict[key_name] = kline_time
                else:
                    pass
            except Exception as e:
                print(e)
                kline_dict[key_name] = kline_time
            del event_dict
            del data
        else:
            del event_dict
            del data
    elif (type == 'depth'):
        data = quote_set.set_depth(db_name, exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            quote_save.wss_save_depth(conn, key_name, timestamp, data)
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            r.publish(channel, json.dumps(event_dict))
            del event_dict
            del data
        else:
            del event_dict
            del data
    return None


def gevent_update_process():
    global conn
    global conn_bar
    global pool
    global kline_dict
    global bars_list
    global bars_period_dict
    global bar_key_name_list

    kline_dict = {}

    period_list = ['3min', '15min', '1hour']
    bar_key_name_list = ['okexf_btc_usd-quarter_kline', 'huobif_btc_usd-quarter_kline']
    bars_list = []
    bars_period_dict = {}
    for period in period_list:
        if ('min' in period):
            bars = int(period.split('min')[0])
        elif ('hour' in period):
            bars = int(period.split('hour')[0]) * 60
        bars_list.append(bars)
        bars_period_dict[bars] = period

    exchange_dict = get_exchange_dict()
    type_list = ['ticker', 'kline', 'depth']
    timestamp = time.time()
    db_name = get_db_name(timestamp)
    conn = sqlite3.connect(db_name, timeout=21)
    conn_bar = sqlite3.connect('dao_quote.db', timeout=21)
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    while True:
        task_list = []
        for exchange in exchange_dict:
            symbol_list = exchange_dict[exchange]
            for symbol in symbol_list:
                for type in type_list:
                    task_list.append(gevent.spawn(set_one_type_symbol, db_name, exchange, symbol, type))
        gevent.joinall(task_list)
        time.sleep(0.3)
        del task_list
        # print(time.time())
        pass


def update_process():
    global kline_dict
    global conn
    global conn_bar

    kline_dict = {}
    exchange_dict = get_exchange_dict()
    type_list = ['ticker', 'kline', 'depth']
    timestamp = time.time()
    db_name = get_db_name(timestamp)
    conn = sqlite3.connect(db_name, timeout=21)
    conn_bar = sqlite3.connect('dao_quote.db', timeout=21)
    while True:
        for exchange in exchange_dict:
            symbol_list = exchange_dict[exchange]
            for symbol in symbol_list:
                for type in type_list:
                    set_one_type_symbol(db_name, exchange, symbol, type)
        time.sleep(0.3)
        # print(time.time())
        pass


def main():
    async_update_process()


if __name__ == '__main__':
    main()
