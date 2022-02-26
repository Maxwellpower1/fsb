# coding=utf-8

import time

from dao_quote.util.exchange_api.binance import api_ba


async def async_ticker(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        data = await api_ba.async_ticker(symbol)
        tick_dict = {}
        tick_dict['last'] = data['lastPrice']
        tick_dict['high'] = data['highPrice']
        tick_dict['low'] = data['lowPrice']
        tick_dict['vol'] = data['volume']
        tick_dict['ask'] = data['askPrice']
        tick_dict['bid'] = data['bidPrice']
        data = tick_dict
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        period = '1min'
        interval = period.lower()[:-2]
        # time_1 = await api_ba.async_time()
        # time_1 = time_1['serverTime']
        time_1 = int(time.time()) * 1000
        interval_seconds = int(interval[:-1]) * 60
        limit = 500
        startTime = time_1 - (interval_seconds * 1000 * limit)
        endTime = time_1
        data_ = await api_ba.async_klines(symbol, interval,
               startTime, endTime, limit)
        data_ = data_[-limit:]
        data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                float(i[4]), float(i[5])] for i in data_]
        del data_
    except Exception as e:
        print(e)
        data = {}
    return data


async def async_depth(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        limit = 10
        data = await api_ba.async_depth(symbol, limit)
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        data = api_ba.ticker(symbol)
        tick_dict = {}
        tick_dict['last'] = data['lastPrice']
        tick_dict['high'] = data['highPrice']
        tick_dict['low'] = data['lowPrice']
        tick_dict['vol'] = data['volume']
        tick_dict['ask'] = data['askPrice']
        tick_dict['bid'] = data['bidPrice']
        data = tick_dict
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        period = '1min'
        interval = period.lower()[:-2]
        time_1 = int(time.time()) * 1000
        interval_seconds = int(interval[:-1]) * 60
        limit = 500
        startTime = time_1 - (interval_seconds * 1000 * limit)
        endTime = time_1
        data_ = api_ba.klines(symbol, interval,
               startTime, endTime, limit)
        data_ = data_[-limit:]
        data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                float(i[4]), float(i[5])] for i in data_]
        del data_
    except Exception as e:
        print(e)
        data = {}
    return data


def depth(symbol):
    '''convert btc_usdt to BTCUSDT
    '''
    try:
        symbol = symbol.replace('_', '').upper()
        limit = 10
        data = api_ba.depth(symbol, limit)
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data
