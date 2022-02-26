# coding=utf-8

import ast
import csv
import json
import time
import sqlite3
import pymongo
import datetime
import traceback
import pandas as pd
from bson import json_util

from dao_quote.settings import config
from dao_quote.vision.order_flow import OrderFlow
from dao_quote.util.convert import convert
from dao_quote.util.exchange_api.okex import api_ok
from dao_quote.util.exchange_api.okexf import api_okf
from dao_quote.util.exchange_api.huobi import api_hb
from dao_quote.util.exchange_api.huobif import api_hbf
from dao_quote.util.exchange_api.binance import api_ba
from dao_quote.util.redis_cache.redis_cache import (get_redis, get_redis_orig)


def get_ticker(request):
    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    return get_ticker_local(exchange, symbol)


def tickers(request):
    exchange = request.GET.get('exchange', None)
    symbol = request.GET.get('symbol', None)
    data = get_ticker_local(exchange, symbol)
    data['date'] = time.time()
    return data


def get_ticker_local(exchange, symbol):
    try:
        key_name = '{}_{}_{}'.format(exchange, symbol, 'ticker')
        value = get_redis_orig(key_name)
        data = ast.literal_eval(value)
    except Exception as e:
        print(key_name)
        if (exchange == 'okex'):
            try:
                data = api_ok.ticker(symbol)['ticker']
            except Exception as e:
                data = {}
        elif (exchange == 'huobi'):
            try:
                data = api_hb.market_detail(symbol)
                data = data['tick']
                data['last'] = data['close']
            except Exception as e:
                data = {}
        elif (exchange == 'binance'):
            try:
                data = api_ba.ticker(symbol)
                tick_dict = {}
                tick_dict['last'] = data['lastPrice']
                tick_dict['high'] = data['highPrice']
                tick_dict['low'] = data['lowPrice']
                tick_dict['vol'] = data['volume']
                data = tick_dict
            except Exception as e:
                data = {}
        else:
            data = {}
    return data


def get_kline(request):
    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    data = get_kline_local(exchange, symbol)
    return data


def klines(request):
    exchange = request.GET.get('exchange', None)
    symbol = request.GET.get('symbol', None)
    data = get_kline_local(exchange, symbol)
    return data


def get_kline_local(exchange, symbol):
    try:
        key_name = '{}_{}_{}'.format(exchange, symbol, 'kline')
        value = get_redis_orig(key_name)
        data = ast.literal_eval(value)
    except Exception as e:
        print(key_name)
        if (exchange == 'OKEX'):
            try:
                type = '1min'
                size = '70'
                since = ''
                data = api_ok.kline(symbol, type, size, since)
            except Exception as e:
                print(e)
                data = {}
        elif (exchange == 'Huobi'):
            try:
                period = '1min'
                size = '70'
                data_ = api_hb.market_history_kline(symbol, period, size)
                data = []
                for k in data_['data']:
                    data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close']])
                data.reverse()
            except Exception as e:
                data = {}
        elif (exchange == 'Binance'):
            try:
                period = '1min'
                interval = period.lower()[:-2]
                time_1 = api_ba.time()['serverTime']
                interval_seconds = int(interval[:-1]) * 60
                startTime = time_1-(interval_seconds * 1000 * 70)
                endTime = time_1
                limit = 70
                data = api_ba.klines(symbol, interval, startTime, endTime, limit)
                data = data[-70:]
            except Exception as e:
                print(e)
                data = {}
        else:
            data = {}
    return data


def get_kline_api(exchange, symbol, period):
    if (exchange.lower() == 'okex'):
        try:
            type = period  # 1min/3min/5min/15min/30min/1hour/2hour/4hour/6hour/12hour
            size = '500'
            since = ''
            data = api_ok.kline(symbol, type, size, since)
        except Exception as e:
            print(e)
            data = {}
    elif (exchange.lower() == 'okexf'):
        try:
            type = period  # 1min/3min/5min/15min/30min/1hour/2hour/4hour/6hour/12hour
            size = '500'
            since = ''
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = api_okf.future_kline(symbol_, type, contract_type, size, since)
        except Exception as e:
            print(e)
            data = {}
    elif (exchange.lower() == 'huobi'):
        try:
            if (period == '1hour'):
                period = '60min'
            else:
                period = period  # 1min, 5min, 15min, 30min, 60min
            size = '500'
            data_ = api_hb.market_history_kline(symbol, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['amount'], k['vol']])
            data.reverse()
        except Exception as e:
            print(e)
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            period = period  # 1min, 5min, 15min, 30min 1hour 4hour
            size = '500'
            data_ = api_hbf.market_history_kline(symbol_, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['vol'], k['amount']])
            # data.reverse()
        except Exception as e:
            data = {}
    elif (exchange.lower() == 'binance'):
        try:
            period = period  # 1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h
            time_1 = int(time.time()) * 1000
            if ('m' in period):
                interval_num = period.lower().split('m')[0]
                interval = interval_num + 'm'
                interval_seconds = int(interval_num) * 60
            elif ('h' in period):
                interval_num = period.lower().split('h')[0]
                interval = interval_num + 'h'
                interval_seconds = int(interval_num) * 60 * 60
            limit = 500
            startTime = time_1 - (interval_seconds * 1000 * limit)
            endTime = time_1
            data = api_ba.klines(symbol, interval, startTime, endTime, limit)
            data = data[-limit:]
        except Exception as e:
            print(e)
            data = {}
    else:
        data = [[1]]
    return data


def get_kline_db(exchange, symbol, period, num, end_timestamp=''):
    if period != '1min':
        type = 'kline.{}'.format(period)
    else:
        type = 'kline'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    if ('min' in period):
        period = int(period.split('min')[0]) * 60
    elif ('hour' in period):
        period = int(period.split('hour')[0]) * 60 * 60
    if (end_timestamp == ''):
        end_timestamp = time.time()
    else:
        pass
    begin_timestamp = end_timestamp - period * int(num)
    try:
        conn = sqlite3.connect('../../../../../dao_quote/dao_quote.db')
    except Exception as e:
        try:
            conn = sqlite3.connect('../../dao_quote/dao_quote.db')
        except Exception as e:
            conn = sqlite3.connect('dao_quote.db')
    c = conn.cursor()
    s = c.execute(('SELECT * FROM (SELECT * FROM "{}" WHERE timestamp<={} '
                   'ORDER BY timestamp DESC LIMIT {}) '
                   'temp ORDER BY timestamp;').format(
                   key_name, end_timestamp*1000, num))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    return data


def get_depth(request):
    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    return get_depth_local(exchange, symbol)


def depths(request):
    exchange = request.GET.get('exchange', None)
    symbol = request.GET.get('symbol', None)
    data = get_depth_local(exchange, symbol)
    data['date'] = time.time()
    return data


def get_depth_local(exchange, symbol):
    try:
        key_name = '{}_{}_{}'.format(exchange, symbol, 'depth')
        value = get_redis_orig(key_name)
        data = ast.literal_eval(value)
    except Exception as e:
        print(key_name)
        if (exchange == 'OKEX'):
            try:
                size = 9
                data = api_ok.depth(symbol, size)
            except Exception as e:
                data = {}
        elif (exchange == 'Huobi'):
            try:
                type = 'step1'
                data = api_hb.market_depth(symbol, type)
                data = data['tick']
                data['asks'].reverse()
            except Exception as e:
                data = {}
        elif (exchange == 'Binance'):
            try:
                limit = 10
                data = api_ba.depth(symbol, limit)
                data['asks'].reverse()
            except Exception as e:
                data = {}
        else:
            data = {}
    return data


def get_spread_line(exchange_a, symbol_a, exchange_b, symbol_b, period='1min'):
    if (period == '1min'):
        klines_a = get_kline_local(exchange_a, symbol_a)
        klines_b = get_kline_local(exchange_b, symbol_b)
    else:
        klines_a = get_kline_api(exchange_a, symbol_a, period)
        klines_b = get_kline_api(exchange_b, symbol_b, period)
    diff_list = []
    if (int(klines_a[-1][0]) > int(klines_b[-1][0])):
        klines_a.pop()
    elif (int(klines_a[-1][0]) < int(klines_b[-1][0])):
        klines_b.pop()
    try:
        for i in range(0, len(klines_a)):
            if (int(klines_a[i][0]) == int(klines_b[i][0])):
                diff = float(klines_a[i][4]) - float(klines_b[i][4])
                vol = float(klines_a[i][5]) - float(klines_b[i][5])
                diff_list.append([klines_a[i][0], diff, vol])
            else:
                continue
    except Exception as e:
        print(e)
    data = diff_list
    return data


def get_backtest_kline_db(exchange, symbol, period, begin_timestamp, end_timestamp):
    '''begin_timestamp & end_timestamp need int or float
    '''
    type = 'kline'
    if exchange == 'stock':
        key_name = '{}_{}_{}.{}'.format(exchange, symbol, type, period)
        period = '1min'
    else:
        key_name = '{}_{}_{}'.format(exchange, symbol, type)
    try:
        conn = sqlite3.connect('dao_quote.db')
    except Exception as e:
        try:
            conn = sqlite3.connect('../dao_quote.db')
        except Exception as e:
            conn = sqlite3.connect('../../dao_quote.db')

    c = conn.cursor()
    s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                   'timestamp<={} ORDER BY timestamp').format(
                   key_name, begin_timestamp*1000, end_timestamp*1000))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    if period != '1min':
        period = int(period.split('min')[0])
        data = convert.combine_lines_3(data, period)
    return data


def get_sqlite_klines_df(exchange, symbol, begin_timestamp, end_timestamp):
    try:
        conn = sqlite3.connect('dao_quote.db')
    except Exception as e:
        conn = sqlite3.connect('../dao_quote.db')
    type = 'kline'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    df = pd.read_sql_query(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                            'timestamp<={} ORDER BY timestamp').format(
                            key_name, begin_timestamp, end_timestamp),
                            con=conn)
    df.columns = map(str.lower, df.columns)
    return df


def get_ticks(exchange, symbol, begin_time, end_time):
    begin_date_list = begin_time.split(' ')[0].split('-')
    begin_year, begin_month, begin_day = begin_date_list
    end_date_list = end_time.split(' ')[0].split('-')
    end_year, end_month, end_day = end_date_list
    end_day_pre = 31
    try:
        data = []
        for year in range(int(begin_year), int(end_year)+1):
            for month in range(int(begin_month), int(end_month)+1):
                if (month == int(end_month)):
                    end_day_pre = int(end_day)
                elif (month > int(begin_month)):
                    begin_day = 1
                for day in range(int(begin_day), int(end_day_pre)+1):
                    if (month == 2):
                        if (day >=28):
                            break
                    if (month not in [1,3,5,7,8,10,12]):
                        if (day >= 31):
                            break
                    db_name = 'docs/quote_{}{:0>2d}{:0>2d}.db'.format(year, month, day)
                    part_data = get_sqlite_ticks_by_db(db_name, exchange, symbol, begin_time, end_time)
                    data += part_data
    except Exception as e:
        data = [str(traceback.format_exc())]
    return data


def get_sqlite_ticks_by_db(db_name, exchange, symbol, begin_time, end_time):
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    type = 'ticker'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    begin_time = convert.to_timestamp(begin_time)
    end_time = convert.to_timestamp(end_time)

    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" LIMIT 2').format(
                       key_name))
        for i in s:
            timestamp = i[1]
            break

        if (timestamp / 10**10 >10):
            begin_time = int(begin_time) * 1000
            end_time = int(end_time) * 1000
        else:
            begin_time = int(begin_time)
            end_time = int(end_time)

        s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                       'timestamp<={} ORDER BY timestamp').format(
                       key_name, begin_time, end_time))
        data = []
        for d in s:
            len_d = len(d)
            tick_dict = {}
            ts = d[1]
            vol = d[7]

            tick_dict['ts'] = ts
            tick_dict['dt'] = datetime.datetime.fromtimestamp(ts/1000)
            tick_dict['t'] = config.HFT_TICKER
            tick_dict['ask'] = d[2]
            if (len_d <= 7):
                tick_dict['bid'] = d[3]
                tick_dict['last'] = d[4]
                tick_dict['high'] = d[5]
                tick_dict['low'] = d[6]
                tick_dict['vol'] = vol
            elif (len_d >= 13):
                vol = d[10]

                tick_dict['a_v'] = d[3]
                tick_dict['bid'] = d[4]
                tick_dict['b_v'] = d[5]
                tick_dict['last'] = d[6]
                tick_dict['open'] = d[7]
                tick_dict['high'] = d[8]
                tick_dict['low'] = d[9]
                tick_dict['vol'] = d[10]
                tick_dict['amt'] = d[11]
                tick_dict['inst'] = d[12]
                if (len_d > 13):
                    tick_dict['pre_close'] = d[13]
                    tick_dict['up_limit'] = d[14]
                    tick_dict['down_limit'] = d[15]
                    if d[24] or d[28]:
                        # if a_v_2 or b_v_2
                        tick_dict['ask_2'] = d[16]
                        tick_dict['ask_3'] = d[17]
                        tick_dict['ask_4'] = d[18]
                        tick_dict['ask_5'] = d[19]
                        tick_dict['bid_2'] = d[20]
                        tick_dict['bid_3'] = d[21]
                        tick_dict['bid_4'] = d[22]
                        tick_dict['bid_5'] = d[23]
                        tick_dict['a_v_2'] = d[24]
                        tick_dict['a_v_3'] = d[25]
                        tick_dict['a_v_4'] = d[26]
                        tick_dict['a_v_5'] = d[27]
                        tick_dict['b_v_2'] = d[28]
                        tick_dict['b_v_3'] = d[29]
                        tick_dict['b_v_4'] = d[30]
                        tick_dict['b_v_5'] = d[31]
            if exchange != 'ctp':
                tick_dict['_id'] = '{}.{}.{}'.format(config.HFT_TICKER, ts, vol)
            data.append(tick_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_csv_ticks(db_name):
    data = []
    with open(db_name) as f:
        reader = csv.reader(f)
        for row in reader:
            if (reader.line_num > 1):
                tick_dict = {}
                ts = datetime.datetime.strptime(row[0][:-3], "%Y-%m-%d %H:%M:%S.%f").timestamp()*1000
                tick_dict['_id'] = '{}.{}'.format(config.HFT_TICKER, ts)
                tick_dict['ts'] = ts
                tick_dict['t'] = config.HFT_TICKER
                tick_dict['ask'] = float(row[6])
                tick_dict['a_v'] = float(row[7])
                tick_dict['bid'] = float(row[4])
                tick_dict['b_v'] = float(row[5])
                tick_dict['last'] = float(row[1])
                tick_dict['open'] = 0.0
                tick_dict['high'] = float(row[2])
                tick_dict['low'] = float(row[3])
                tick_dict['vol'] = float(row[8])
                tick_dict['amt'] = float(row[9])
                tick_dict['inst'] = float(row[10])
                data.append(tick_dict)
    return data


def get_all_ticks(db_name, exchange, symbol):
    type = 'ticker'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(
        # s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp LIMIT 100').format(
                       key_name))
        data = []
        for d in s:
            tick_dict = {}
            ts = d[1]
            tick_dict['_id'] = '{}.{}'.format(config.HFT_TICKER, ts)
            tick_dict['ts'] = ts
            tick_dict['t'] = config.HFT_TICKER
            tick_dict['ask'] = d[2]
            if (len(d) <= 7):
                tick_dict['bid'] = d[3]
                tick_dict['last'] = d[4]
                tick_dict['high'] = d[5]
                tick_dict['low'] = d[6]
                tick_dict['vol'] = d[7]
            else:
                tick_dict['a_v'] = d[3]
                tick_dict['bid'] = d[4]
                tick_dict['b_v'] = d[5]
                tick_dict['last'] = d[6]
                tick_dict['open'] = d[7]
                tick_dict['high'] = d[8]
                tick_dict['low'] = d[9]
                tick_dict['vol'] = d[10]
                tick_dict['amt'] = d[11]
                tick_dict['inst'] = d[12]
            data.append(tick_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_depths(exchange, symbol, begin_time, end_time):
    begin_date_list = begin_time.split(' ')[0].split('-')
    begin_year, begin_month, begin_day = begin_date_list
    end_date_list = end_time.split(' ')[0].split('-')
    end_year, end_month, end_day = end_date_list
    end_day_pre = 31
    try:
        data = []
        for year in range(int(begin_year), int(end_year)+1):
            for month in range(int(begin_month), int(end_month)+1):
                if (month == int(end_month)):
                    end_day_pre = int(end_day)
                elif (month > int(begin_month)):
                    begin_day = 1
                for day in range(int(begin_day), int(end_day_pre)+1):
                    if (month == 2):
                        if (day >=28):
                            break
                    if (month not in [1,3,5,7,8,10,12]):
                        if (day >= 31):
                            break
                    db_name = 'docs/quote_{}{:0>2d}{:0>2d}.db'.format(year, month, day)
                    part_data = get_sqlite_depths_by_db(db_name, exchange, symbol, begin_time, end_time)
                    data += part_data
    except Exception as e:
        data = [str(traceback.format_exc())]
    return data


def get_sqlite_depths_by_db(db_name, exchange, symbol, begin_time, end_time):
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    type = 'depth'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    begin_time = convert.to_timestamp(begin_time)
    end_time = convert.to_timestamp(end_time)

    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" LIMIT 2').format(
                       key_name))
        for i in s:
            timestamp = i[1]
            break

        if (timestamp / 10**10 >10):
            begin_time = int(begin_time) * 1000
            end_time = int(end_time) * 1000
        else:
            begin_time = int(begin_time)
            end_time = int(end_time)

        s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                       'timestamp<={} ORDER BY timestamp').format(
                       key_name, begin_time, end_time))
        data = []
        for d in s:
            depth_dict = {}
            ts = d[1]
            depth_dict['_id'] = '{}.{}'.format(config.HFT_DEPTH, ts)
            depth_dict['ts'] = ts
            depth_dict['t'] = config.HFT_DEPTH
            depth_dict['asks'] = eval(str(d[2]))
            depth_dict['bids'] = eval(str(d[3]))
            data.append(depth_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_all_depths(db_name, exchange, symbol):
    type = 'depth'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(
        # s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp LIMIT 100').format(
                       key_name))
        data = []
        for d in s:
            depth_dict = {}
            ts = d[1]
            depth_dict['_id'] = '{}.{}'.format(config.HFT_DEPTH, ts)
            depth_dict['ts'] = ts
            depth_dict['t'] = config.HFT_DEPTH
            depth_dict['asks'] = eval(str(d[2]))
            depth_dict['bids'] = eval(str(d[3]))
            data.append(depth_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_depthalls(exchange, symbol, begin_time, end_time):
    begin_date_list = begin_time.split(' ')[0].split('-')
    begin_year, begin_month, begin_day = begin_date_list
    end_date_list = end_time.split(' ')[0].split('-')
    end_year, end_month, end_day = end_date_list
    end_day_pre = 31
    try:
        data = []
        for year in range(int(begin_year), int(end_year)+1):
            for month in range(int(begin_month), int(end_month)+1):
                if (month == int(end_month)):
                    end_day_pre = int(end_day)
                elif (month > int(begin_month)):
                    begin_day = 1
                for day in range(int(begin_day), int(end_day_pre)+1):
                    if (month == 2):
                        if (day >=28):
                            break
                    if (month not in [1,3,5,7,8,10,12]):
                        if (day >= 31):
                            break
                    db_name = 'docs/quote_{}{:0>2d}{:0>2d}.db'.format(year, month, day)
                    part_data = get_sqlite_depthalls_by_db(db_name, exchange, symbol, begin_time, end_time)
                    data += part_data
    except Exception as e:
        data = [str(traceback.format_exc())]
    return data


def get_sqlite_depthalls_by_db(db_name, exchange, symbol, begin_time, end_time):
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    type = 'depthall'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    begin_time = convert.to_timestamp(begin_time)
    end_time = convert.to_timestamp(end_time)

    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" LIMIT 2').format(
                       key_name))
        for i in s:
            timestamp = i[1]
            break

        if (timestamp / 10**10 >10):
            begin_time = int(begin_time) * 1000
            end_time = int(end_time) * 1000
        else:
            begin_time = int(begin_time)
            end_time = int(end_time)

        s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                       'timestamp<={} ORDER BY timestamp').format(
                       key_name, begin_time, end_time))
        data = []
        for d in s:
            depth_dict = {}
            ts = d[1]
            depth_dict['_id'] = '{}.{}'.format(config.HFT_DEPTHALL, ts)
            depth_dict['ts'] = ts
            depth_dict['t'] = config.HFT_DEPTHALL
            depth_dict['asks'] = eval(str(d[2]))
            depth_dict['bids'] = eval(str(d[3]))
            data.append(depth_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_all_depthalls(db_name, exchange, symbol):
    type = 'depthall'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(
                       key_name))
        data = []
        for d in s:
            depth_dict = {}
            ts = d[1]
            depth_dict['_id'] = '{}.{}'.format(config.HFT_DEPTHALL, ts)
            depth_dict['ts'] = ts
            depth_dict['t'] = config.HFT_DEPTHALL
            depth_dict['asks'] = eval(str(d[2]))
            depth_dict['bids'] = eval(str(d[3]))
            data.append(depth_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_trades(exchange, symbol, begin_time, end_time):
    begin_date_list = begin_time.split(' ')[0].split('-')
    begin_year, begin_month, begin_day = begin_date_list
    end_date_list = end_time.split(' ')[0].split('-')
    end_year, end_month, end_day = end_date_list
    end_day_pre = 31
    try:
        data = []
        for year in range(int(begin_year), int(end_year)+1):
            for month in range(int(begin_month), int(end_month)+1):
                if (month == int(end_month)):
                    end_day_pre = int(end_day)
                elif (month > int(begin_month)):
                    begin_day = 1
                for day in range(int(begin_day), int(end_day_pre)+1):
                    if (month == 2):
                        if (day >=28):
                            break
                    if (month not in [1,3,5,7,8,10,12]):
                        if (day >= 31):
                            break
                    db_name = 'docs/quote_{}{:0>2d}{:0>2d}.db'.format(year, month, day)
                    part_data = get_sqlite_trades_by_db(db_name, exchange, symbol, begin_time, end_time)
                    data += part_data
    except Exception as e:
        data = [str(traceback.format_exc())]
    return data


def get_sqlite_trades_by_db(db_name, exchange, symbol, begin_time, end_time):
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    type = 'trade'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    begin_time = convert.to_timestamp(begin_time)
    end_time = convert.to_timestamp(end_time)

    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" LIMIT 2').format(
                       key_name))
        for i in s:
            timestamp = i[1]
            break

        if (timestamp / 10**10 >10):
            begin_time = int(begin_time) * 1000
            end_time = int(end_time) * 1000
        else:
            begin_time = int(begin_time)
            end_time = int(end_time)

        s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                       'timestamp<={} ORDER BY timestamp').format(
                       key_name, begin_time, end_time))
        data = []
        for d in s:
            trade_dict = {}
            ts = d[1]
            trade_dict['_id'] = '{}.{}'.format(config.HFT_TRADE, ts)
            trade_dict['ts'] = ts
            trade_dict['t'] = config.HFT_TRADE
            trade_dict['trade_id'] = int(d[2])
            trade_dict['price'] = float(d[3])
            trade_dict['size'] = float(d[4])
            trade_dict['side'] = d[5]
            data.append(trade_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_all_trades(db_name, exchange, symbol):
    type = 'trade'
    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    try:
        conn = sqlite3.connect('{}'.format(db_name))
    except Exception as e:
        print('db_name: {} not found'.format(db_name))
    c = conn.cursor()
    try:
        s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(
                       key_name))
        data = []
        for d in s:
            trade_dict = {}
            ts = d[1]
            trade_dict['_id'] = '{}.{}'.format(config.HFT_TRADE, ts)
            trade_dict['ts'] = ts
            trade_dict['t'] = config.HFT_TRADE
            trade_dict['trade_id'] = int(d[2])
            trade_dict['price'] = float(d[3])
            trade_dict['size'] = float(d[4])
            trade_dict['side'] = d[5]
            data.append(trade_dict)
    except Exception as e:
        data = []
        # print(db_name, key_name, traceback.format_exc())
        print(db_name, key_name, str(e))
    return data


def get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp):
    collection = '{}_{}_hfd'.format(exchange, symbol)
    rst = db[collection].find({
              'ts':{
                  '$gte': int(begin_timestamp)*1000,
                  '$lt': int(end_timestamp)*1000
               },
               "t": {"$in": type_list}
          }, {'_id': 0}).sort([('ts', pymongo.ASCENDING), ('vol', pymongo.ASCENDING)])
    rst = json_util.dumps(rst)
    return rst


def get_trade_dict_list(db, exchange, symbol, begin_timestamp, end_timestamp, json_format=True):
    type_list = [config.HFT_TICKER]
    tick_dict_list = get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp)
    tick_dict_list = json.loads(tick_dict_list)
    of = OrderFlow(print_msg=False)
    trade_dict_list = of.tick_2_trade_list(tick_dict_list)
    if json_format:
        trade_dict_list = json.dumps(trade_dict_list)
    return trade_dict_list
